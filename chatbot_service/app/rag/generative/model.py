import os
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    pipeline,
)
from peft import PeftModel, PeftConfig

from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline

logger = logging.getLogger(__name__)

# =========================
# CẤU HÌNH
# =========================
@dataclass
class GenerativeConfig:
    # Base model từ HuggingFace Hub
    base_model_id: str = "Qwen/Qwen2.5-0.5B-Instruct"
    
    # Đường dẫn LoRA adapter (tương đối hoặc tuyệt đối)
    lora_path: str = "app/rag/generative/model/qwen-500m-qlora-xpervia/final"  # Sử dụng final checkpoint
    
    device: Optional[str] = None  # "cuda" | "cpu" | None (tự phát hiện)
    dtype: str = "auto"           # "auto" | "float16" | "float32"
    trust_remote_code: bool = True

    # QLoRA (4-bit) - khuyến nghị True để tiết kiệm VRAM
    load_in_4bit: bool = True
    bnb_4bit_quant_type: str = "nf4"
    bnb_4bit_compute_dtype: str = "float16"
    bnb_4bit_use_double_quant: bool = True

    # Merge adapter vào base model (khuyến nghị False để linh hoạt hơn)
    merge_adapters: bool = False

    # Tham số sinh text
    gen_kwargs: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

        if self.gen_kwargs is None:
            self.gen_kwargs = {
                "do_sample": True,
                "temperature": 0.7,
                "top_p": 0.9,
                "repetition_penalty": 1.1,
                "max_new_tokens": 512,
                "pad_token_id": None,  # Sẽ được set trong _build_pipeline
            }
        
        # Resolve đường dẫn LoRA thành absolute path
        if not os.path.isabs(self.lora_path):
            # Tính từ vị trí file này
            current_dir = Path(__file__).parent
            self.lora_path = str(current_dir / self.lora_path)

# =========================
# LOADER
# =========================
class QwenLoraLoader:
    """
    Loader cho base Qwen + áp dụng LoRA adapter từ local path.
    - Hỗ trợ CPU/GPU
    - Hỗ trợ 4-bit (QLoRA) khi load_in_4bit=True
    - Có thể merge adapter nếu cần (merge_adapters=True)
    """

    def __init__(self, cfg: GenerativeConfig):
        self.cfg = cfg
        self.tokenizer = None
        self.model = None
        self.pipe = None

    def _resolve_dtype(self):
        if self.cfg.dtype == "float16":
            return torch.float16
        elif self.cfg.dtype == "float32":
            return torch.float32
        else:  # "auto"
            return torch.float16 if self.cfg.device == "cuda" else torch.float32

    def _validate_lora_path(self):
        """Kiểm tra LoRA path có hợp lệ không"""
        if not os.path.exists(self.cfg.lora_path):
            raise FileNotFoundError(f"LoRA adapter path không tồn tại: {self.cfg.lora_path}")
        
        # Kiểm tra có adapter_config.json
        adapter_config_path = os.path.join(self.cfg.lora_path, "adapter_config.json")
        if not os.path.exists(adapter_config_path):
            raise FileNotFoundError(f"Không tìm thấy adapter_config.json trong: {self.cfg.lora_path}")
        
        logger.info(f"✅ LoRA adapter path hợp lệ: {self.cfg.lora_path}")

    def _load_tokenizer(self):
        """Load tokenizer từ LoRA path hoặc base model"""
        # Ưu tiên tải từ LoRA path (có thể có tokenizer đã fine-tuned)
        try:
            if os.path.exists(self.cfg.lora_path):
                logger.info(f"Loading tokenizer from LoRA path: {self.cfg.lora_path}")
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.cfg.lora_path, 
                    use_fast=True, 
                    trust_remote_code=self.cfg.trust_remote_code
                )
            else:
                raise FileNotFoundError("LoRA path not found, fallback to base model")
        except Exception as e:
            # Fallback sang base model
            logger.warning(f"Failed to load tokenizer from LoRA path: {e}")
            logger.info(f"Loading tokenizer from base model: {self.cfg.base_model_id}")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.cfg.base_model_id, 
                use_fast=True, 
                trust_remote_code=self.cfg.trust_remote_code
            )

        # Đảm bảo có pad_token
        if self.tokenizer.pad_token is None:
            if self.tokenizer.eos_token is not None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                logger.info(f"Set pad_token = eos_token: {self.tokenizer.eos_token}")
            else:
                # Fallback cho Qwen
                self.tokenizer.pad_token = "<|endoftext|>"
                logger.info("Set pad_token = <|endoftext|>")

    def _load_base_model(self):
        """Load base model từ HuggingFace Hub"""
        dtype = self._resolve_dtype()

        # Cấu hình quantization nếu cần
        quant_config = None
        if self.cfg.load_in_4bit:
            compute_dtype = torch.float16 if self.cfg.bnb_4bit_compute_dtype == "float16" else torch.bfloat16
            quant_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type=self.cfg.bnb_4bit_quant_type,
                bnb_4bit_compute_dtype=compute_dtype,
                bnb_4bit_use_double_quant=self.cfg.bnb_4bit_use_double_quant,
            )
            logger.info("✅ 4-bit quantization enabled")

        logger.info(f"Loading base model: {self.cfg.base_model_id}")
        logger.info(f"   Device: {self.cfg.device}")
        logger.info(f"   Dtype: {dtype}")
        logger.info(f"   4-bit: {self.cfg.load_in_4bit}")

        self.model = AutoModelForCausalLM.from_pretrained(
            self.cfg.base_model_id,
            torch_dtype=dtype,
            device_map="auto" if self.cfg.device == "cuda" else None,
            trust_remote_code=self.cfg.trust_remote_code,
            quantization_config=quant_config,
            low_cpu_mem_usage=True,
        )
        
        # Enable cache for inference
        self.model.config.use_cache = True
        logger.info("✅ Base model loaded successfully")

    def _apply_lora(self):
        """Apply LoRA adapter lên base model"""
        # Validate LoRA path trước
        self._validate_lora_path()
        
        # Đọc PeftConfig để kiểm tra compatibility
        try:
            peft_config = PeftConfig.from_pretrained(self.cfg.lora_path)
            logger.info(f"LoRA config: {peft_config}")
            
            # Warning nếu base model khác nhau
            if hasattr(peft_config, 'base_model_name_or_path'):
                config_base = peft_config.base_model_name_or_path
                if config_base and config_base != self.cfg.base_model_id:
                    logger.warning(
                        f"⚠️  LoRA adapter được train trên: {config_base}"
                        f"Bạn đang dùng base model: {self.cfg.base_model_id}"
                        f"Có thể gây ra vấn đề compatibility!"
                    )
        except Exception as e:
            logger.warning(f"Cannot read PeftConfig: {e}")

        logger.info(f"Applying LoRA adapter from: {self.cfg.lora_path}")
        self.model = PeftModel.from_pretrained(self.model, self.cfg.lora_path)

        if self.cfg.merge_adapters:
            logger.info("🔄 Merging LoRA adapters into base weights...")
            self.model = self.model.merge_and_unload()
            logger.info("✅ LoRA adapters merged successfully")
        else:
            logger.info("✅ LoRA adapter applied (not merged)")

        # Set to eval mode
        self.model.eval()

    def _build_pipeline(self):
        """Tạo HuggingFace pipeline cho text generation"""
        logger.info("Building HuggingFace text-generation pipeline...")
        
        # Update gen_kwargs với pad_token_id
        gen_kwargs = dict(self.cfg.gen_kwargs)
        if gen_kwargs.get("pad_token_id") is None:
            gen_kwargs["pad_token_id"] = self.tokenizer.pad_token_id
        
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if self.cfg.device == "cuda" and torch.cuda.is_available() else -1,
            **gen_kwargs,
        )
        logger.info("✅ Pipeline built successfully")

    def load(self):
        """Load toàn bộ: tokenizer + base model + LoRA + pipeline"""
        try:
            self._load_tokenizer()
            self._load_base_model()
            self._apply_lora()
            self._build_pipeline()
            logger.info("🎉 QwenLoraLoader completed successfully!")
            return self.tokenizer, self.pipe
        except Exception as e:
            logger.error(f"❌ QwenLoraLoader failed: {e}")
            raise

# =========================
# API PUBLIC CHO RAG
# =========================
def build_chat_model(cfg: Optional[GenerativeConfig] = None) -> ChatHuggingFace:
    """
    Tạo ChatHuggingFace từ base Qwen + LoRA adapter local.
    
    Args:
        cfg: GenerativeConfig instance. Nếu None sẽ dùng default config.
        
    Returns:
        ChatHuggingFace instance sẵn sàng cho RAG pipeline
        
    Raises:
        Exception: Nếu không thể load model hoặc LoRA adapter
    """
    if cfg is None:
        cfg = GenerativeConfig()

    # Load model với LoRA
    loader = QwenLoraLoader(cfg)
    tokenizer, hf_pipeline = loader.load()

    # Wrap thành LangChain LLM
    langchain_llm = HuggingFacePipeline(pipeline=hf_pipeline)

    # Tạo ChatHuggingFace (giữ chat_template có sẵn của Qwen)
    chat_model = ChatHuggingFace(
        llm=langchain_llm,
        verbose=False,  # Set True nếu muốn debug
    )
    
    logger.info("✅ ChatHuggingFace created successfully with fine-tuned Qwen model")
    return chat_model


def get_model_info(cfg: Optional[GenerativeConfig] = None) -> Dict[str, Any]:
    """
    Lấy thông tin model để debug/logging
    
    Args:
        cfg: GenerativeConfig instance
        
    Returns:
        Dict chứa thông tin model, tokenizer, config, etc.
    """
    try:
        if cfg is None:
            cfg = GenerativeConfig()

        # Thử load tokenizer để lấy info
        try:
            tokenizer = AutoTokenizer.from_pretrained(
                cfg.lora_path if os.path.exists(cfg.lora_path) else cfg.base_model_id,
                trust_remote_code=cfg.trust_remote_code
            )
            tokenizer_info = {
                "vocab_size": len(tokenizer),
                "pad_token": tokenizer.pad_token,
                "eos_token": tokenizer.eos_token,
                "bos_token": getattr(tokenizer, 'bos_token', None),
                "has_chat_template": hasattr(tokenizer, 'chat_template') and tokenizer.chat_template is not None,
                "model_max_length": getattr(tokenizer, 'model_max_length', None),
            }
        except Exception as e:
            tokenizer_info = {"error": str(e)}

        return {
            "base_model_id": cfg.base_model_id,
            "lora_path": cfg.lora_path,
            "lora_path_exists": os.path.exists(cfg.lora_path),
            "device": cfg.device,
            "dtype": cfg.dtype,
            "load_in_4bit": cfg.load_in_4bit,
            "merge_adapters": cfg.merge_adapters,
            "gen_kwargs": cfg.gen_kwargs,
            "tokenizer_info": tokenizer_info,
            "cuda_available": torch.cuda.is_available(),
            "torch_version": torch.__version__,
        }
    except Exception as e:
        return {"error": str(e)}


def create_model_summary(cfg: GenerativeConfig) -> Dict[str, Any]:
    """
    Tạo summary chi tiết để logging
    
    Args:
        cfg: GenerativeConfig instance
        
    Returns:
        Dict chứa summary đầy đủ
    """
    import psutil
    from dataclasses import asdict
    
    return {
        "config": asdict(cfg),
        "model_info": get_model_info(cfg),
        "system_info": {
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
            "gpu_available": torch.cuda.is_available(),
            "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        }
    }