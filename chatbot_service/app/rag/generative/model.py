import os
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
from app import config

LORA_ADAPTER_PATH = "model/qwen2_5_0_5b_lora_ragqa"

@dataclass
class GenerativeConfig:
    base_model_id: str = config.LLM_MODEL
    lora_path: str = LORA_ADAPTER_PATH
    dtype: str = "auto"
    trust_remote_code: bool = True
    load_in_4bit: bool = True
    bnb_4bit_quant_type: str = "nf4"
    bnb_4bit_compute_dtype: str = "float16"
    bnb_4bit_use_double_quant: bool = True
    merge_adapters: bool = True
    gen_kwargs: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.gen_kwargs is None:
            self.gen_kwargs = {
                "do_sample": True,
                "temperature": 0.7,
                "top_p": 0.9,
                "repetition_penalty": 1.1,
                "max_new_tokens": 512,
                "pad_token_id": None,
            }
        
        # Resolve đường dẫn LoRA thành absolute path
        if not os.path.isabs(self.lora_path):
            current_dir = Path(__file__).parent
            self.lora_path = str(current_dir / self.lora_path)

class QwenLoraLoader:
    def __init__(self, cfg: GenerativeConfig):
        self.cfg = cfg
        self.tokenizer = None
        self.model = None
        self.pipe = None

    def _resolve_dtype(self):
        if self.cfg.dtype == "float16":
            return torch.float16
        else:
            return torch.float32

    def _validate_lora_path(self):
        if not os.path.exists(self.cfg.lora_path):
            raise FileNotFoundError(f"LoRA adapter path không tồn tại: {self.cfg.lora_path}")
        
        adapter_config_path = os.path.join(self.cfg.lora_path, "adapter_config.json")
        if not os.path.exists(adapter_config_path):
            raise FileNotFoundError(f"Không tìm thấy adapter_config.json trong: {self.cfg.lora_path}")

    def _load_tokenizer(self):
        try:
            if os.path.exists(self.cfg.lora_path):
                print(f"Loading tokenizer from LoRA path: {self.cfg.lora_path}")
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.cfg.lora_path, 
                    use_fast=True, 
                    trust_remote_code=self.cfg.trust_remote_code
                )
            else:
                raise FileNotFoundError("LoRA path not found, fallback to base model")
        except Exception as e:
            print(f"Failed to load tokenizer from LoRA path: {e}")
            print(f"Loading tokenizer from base model: {self.cfg.base_model_id}")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.cfg.base_model_id, 
                use_fast=True, 
                trust_remote_code=self.cfg.trust_remote_code
            )

        # Đảm bảo có pad_token
        if self.tokenizer.pad_token is None:
            if self.tokenizer.eos_token is not None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                print(f"Set pad_token = eos_token: {self.tokenizer.eos_token}")
            else:
                # Fallback cho Qwen
                self.tokenizer.pad_token = "<|endoftext|>"
                print("Set pad_token = <|endoftext|>")

    def _load_base_model(self):
        dtype = self._resolve_dtype()
        quant_config = None
        if self.cfg.load_in_4bit:
            compute_dtype = torch.float16 if self.cfg.bnb_4bit_compute_dtype == "float16" else torch.bfloat16
            quant_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type=self.cfg.bnb_4bit_quant_type,
                bnb_4bit_compute_dtype=compute_dtype,
                bnb_4bit_use_double_quant=self.cfg.bnb_4bit_use_double_quant,
            )
            print("[SUCCESSFUL] 4-bit quantization enabled")

        print(f"Loading base model: {self.cfg.base_model_id}")
        print(f"   Dtype: {dtype}")   
        print(f"   4-bit: {self.cfg.load_in_4bit}")

        self.model = AutoModelForCausalLM.from_pretrained(
            self.cfg.base_model_id,
            torch_dtype=dtype,
            trust_remote_code=self.cfg.trust_remote_code,
            quantization_config=quant_config,
            low_cpu_mem_usage=True,
        )
        
        # Enable cache for inference
        self.model.config.use_cache = True
        print("[SUCCESSFUL] Base model loaded successfully")

    def _apply_lora(self):
        self._validate_lora_path()
        
        try:
            peft_config = PeftConfig.from_pretrained(self.cfg.lora_path)
            print(f"LoRA config: {peft_config}")
            
            # Warning nếu base model khác nhau
            if hasattr(peft_config, 'base_model_name_or_path'):
                config_base = peft_config.base_model_name_or_path
                if config_base and config_base != self.cfg.base_model_id:
                    print(
                        f"⚠️  LoRA adapter được train trên: {config_base}"
                        f"Bạn đang dùng base model: {self.cfg.base_model_id}"
                        f"Có thể gây ra vấn đề compatibility!"
                    )
        except Exception as e:
            print(f"Cannot read PeftConfig: {e}")

        print(f"Applying LoRA adapter from: {self.cfg.lora_path}")
        self.model = PeftModel.from_pretrained(self.model, self.cfg.lora_path)

        if self.cfg.merge_adapters:
            self.model = self.model.merge_and_unload()
            print("[SUCCESSFUL] LoRA adapters merged successfully")
        else:
            print("[SUCCESSFUL] LoRA adapter applied (not merged)")
        self.model.eval()

    def _build_pipeline(self):
        print("Building HuggingFace text-generation pipeline...")

        gen_kwargs = dict(self.cfg.gen_kwargs)
        if gen_kwargs.get("pad_token_id") is None:
            gen_kwargs["pad_token_id"] = self.tokenizer.pad_token_id
        
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            **gen_kwargs,
        )
        print("[SUCCESSFUL] Pipeline built successfully")

    def load(self):
        try:
            self._load_tokenizer()
            self._load_base_model()
            self._apply_lora()
            self._build_pipeline()
            print("[SUCCESSFUL] QwenLoraLoader completed successfully!")
            return self.tokenizer, self.pipe
        except Exception as e:
            print(f"QwenLoraLoader failed: {e}")
            raise e

def build_chat_model(cfg: Optional[GenerativeConfig] = None) -> ChatHuggingFace:
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
        verbose=True,  # Set True nếu muốn debug
    )

    print("[SUCCESSFUL] ChatHuggingFace created successfully with fine-tuned Qwen model")
    return chat_model