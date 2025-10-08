import os
import time
import psutil
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import asdict

from .model import GenerativeConfig, get_model_info

logger = logging.getLogger(__name__)

def measure_generation_performance(
    generation_func: Callable,
    *args,
    **kwargs
) -> Dict[str, Any]:
    """
    Đo performance của quá trình generation
    
    Args:
        generation_func: Hàm generation cần đo
        *args, **kwargs: Arguments cho hàm
        
    Returns:
        Dict chứa kết quả và metrics performance
    """
    
    # Đo memory và CPU trước khi chạy
    process = psutil.Process()
    memory_before = process.memory_info().rss / 1024 / 1024  # MB
    cpu_before = process.cpu_percent(interval=None)
    
    start_time = time.time()
    
    try:
        # Chạy generation function
        result = generation_func(*args, **kwargs)
        success = True
        error = None
        
    except Exception as e:
        result = None
        success = False
        error = str(e)
        logger.error(f"Generation failed: {error}")
    
    end_time = time.time()
    
    # Đo memory và CPU sau khi chạy
    memory_after = process.memory_info().rss / 1024 / 1024  # MB
    cpu_after = process.cpu_percent(interval=None)
    
    metrics = {
        "success": success,
        "result": result,
        "error": error,
        "duration_seconds": round(end_time - start_time, 3),
        "memory_before_mb": round(memory_before, 2),
        "memory_after_mb": round(memory_after, 2),
        "memory_delta_mb": round(memory_after - memory_before, 2),
        "cpu_before_percent": cpu_before,
        "cpu_after_percent": cpu_after,
    }
    
    # Thêm metrics cho text nếu có
    if result and isinstance(result, str):
        metrics.update({
            "result_length_chars": len(result),
            "result_length_words": len(result.split()),
            "generation_speed_chars_per_sec": round(len(result) / (end_time - start_time), 2) if (end_time - start_time) > 0 else 0,
            "generation_speed_words_per_sec": round(len(result.split()) / (end_time - start_time), 2) if (end_time - start_time) > 0 else 0,
        })
    
    return metrics

def validate_model_config(config: GenerativeConfig) -> List[str]:
    """
    Validate cấu hình model
    
    Args:
        config: GenerativeConfig instance
        
    Returns:
        List of validation error messages (empty list nếu OK)
    """
    errors = []
    
    # Kiểm tra base_model_id
    if not config.base_model_id:
        errors.append("base_model_id cannot be empty")
    
    # Kiểm tra lora_path
    if not config.lora_path:
        errors.append("lora_path cannot be empty")
    elif not os.path.exists(config.lora_path):
        errors.append(f"lora_path does not exist: {config.lora_path}")
    
    # Kiểm tra device
    if config.device not in ["cpu", "cuda", "auto", None]:
        errors.append(f"Invalid device: {config.device}")
    
    # Kiểm tra gen_kwargs
    if config.gen_kwargs:
        numeric_fields = ["max_new_tokens", "temperature", "top_p", "repetition_penalty"]
        for field in numeric_fields:
            if field in config.gen_kwargs:
                value = config.gen_kwargs[field]
                if not isinstance(value, (int, float)):
                    errors.append(f"{field} must be numeric, got {type(value)}")
                elif field == "max_new_tokens" and value <= 0:
                    errors.append(f"{field} must be positive")
                elif field in ["temperature", "top_p"] and (value < 0 or value > 2):
                    errors.append(f"{field} should be between 0 and 2")
    
    return errors

def create_model_summary(config: GenerativeConfig) -> Dict[str, Any]:
    """
    Tạo summary thông tin model để logging/debug
    
    Args:
        config: GenerativeConfig instance
        
    Returns:
        Dict chứa thông tin tổng hợp
    """
    import torch
    
    summary = {
        "config": asdict(config),
        "validation_errors": validate_model_config(config),
        "model_info": get_model_info(config),
        "system_info": {
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": round(psutil.virtual_memory().total / 1024**3, 2),
            "memory_available_gb": round(psutil.virtual_memory().available / 1024**3, 2),
            "cuda_available": torch.cuda.is_available(),
            "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        }
    }
    
    # Thêm thông tin GPU nếu có
    if torch.cuda.is_available():
        try:
            gpu_info = {}
            for i in range(torch.cuda.device_count()):
                gpu_info[f"gpu_{i}"] = {
                    "name": torch.cuda.get_device_name(i),
                    "memory_total_gb": round(torch.cuda.get_device_properties(i).total_memory / 1024**3, 2),
                }
            summary["gpu_info"] = gpu_info
        except Exception as e:
            summary["gpu_info"] = {"error": str(e)}
    
    return summary

def estimate_context_tokens(text: str, approximate: bool = True) -> int:
    """
    Ước tính số tokens trong text
    
    Args:
        text: Input text
        approximate: Sử dụng phương pháp xấp xỉ (nhanh) hay chính xác (chậm)
        
    Returns:
        Estimated number of tokens
    """
    if not text:
        return 0
    
    if approximate:
        # Phương pháp xấp xỉ cho tiếng Việt: ~2.5 chars per token
        return max(1, len(text) // 3)
    
    else:
        # Phương pháp chính xác: dùng tokenizer thực (chậm hơn)
        try:
            from transformers import AutoTokenizer
            tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
            tokens = tokenizer.tokenize(text)
            return len(tokens)
        except Exception as e:
            logger.warning(f"Cannot use exact tokenization, fallback to approximation: {e}")
            return max(1, len(text) // 3)

def truncate_context_if_needed(
    context: str,
    max_tokens: int,
    question: str = "",
    preserve_ratio: float = 0.8
) -> str:
    """
    Cắt ngắn context nếu quá dài để fit vào context window
    
    Args:
        context: Context text cần cắt
        max_tokens: Giới hạn tokens tối đa
        question: Câu hỏi (để tính toán space còn lại)
        preserve_ratio: Tỷ lệ context được giữ lại (0.8 = 80%)
        
    Returns:
        Truncated context
    """
    
    # Tính toán tokens
    question_tokens = estimate_context_tokens(question)
    context_tokens = estimate_context_tokens(context)
    
    # Dự trữ space cho output và overhead
    reserved_tokens = 512 + 100  # 512 cho output + 100 cho overhead
    available_tokens = max_tokens - question_tokens - reserved_tokens
    
    if context_tokens <= available_tokens:
        return context  # Không cần cắt
    
    # Cắt context về kích thước phù hợp
    target_tokens = int(available_tokens * preserve_ratio)
    target_chars = target_tokens * 3  # xấp xỉ ngược lại (3 chars per token)
    
    if target_chars >= len(context):
        return context
    
    # Cắt tại word boundary để tránh cắt giữa từ
    truncated = context[:target_chars].rsplit(' ', 1)[0]
    truncated += "\n\n[...Nội dung đã được rút gọn để phù hợp với giới hạn token...]"
    
    logger.info(f"Context truncated: {context_tokens} -> {estimate_context_tokens(truncated)} tokens")
    
    return truncated

def format_generation_log(
    question: str,
    context_length: int,
    answer: str,
    duration: float,
    model_config: Optional[GenerativeConfig] = None
) -> str:
    """
    Format log entry cho việc generation
    
    Args:
        question: User question
        context_length: Length of context used
        answer: Generated answer
        duration: Generation duration in seconds
        model_config: Model configuration
        
    Returns:
        Formatted log string
    """
    
    log_parts = [
        f"=== GENERATION LOG ===",
        f"Question: {question[:100]}{'...' if len(question) > 100 else ''}",
        f"Context length: {context_length} chars (~{estimate_context_tokens(str(context_length))} tokens)",
        f"Answer length: {len(answer)} chars (~{estimate_context_tokens(answer)} tokens)",
        f"Duration: {duration:.3f}s",
    ]
    
    if duration > 0:
        words_per_sec = len(answer.split()) / duration
        chars_per_sec = len(answer) / duration
        log_parts.extend([
            f"Speed: {words_per_sec:.1f} words/sec, {chars_per_sec:.1f} chars/sec"
        ])
    
    if model_config:
        log_parts.extend([
            f"Base model: {model_config.base_model_id}",
            f"LoRA: {os.path.basename(model_config.lora_path)}",
            f"Device: {model_config.device}",
            f"4-bit: {model_config.load_in_4bit}",
        ])
    
    log_parts.append("=" * 50)
    
    return "\n".join(log_parts)

def check_model_compatibility(config: GenerativeConfig) -> Dict[str, Any]:
    """
    Kiểm tra compatibility giữa base model và LoRA adapter
    
    Args:
        config: GenerativeConfig instance
        
    Returns:
        Dict với kết quả kiểm tra
    """
    import os
    import json
    from pathlib import Path
    
    result = {
        "compatible": True,
        "warnings": [],
        "errors": [],
        "info": {}
    }
    
    try:
        # Kiểm tra LoRA path
        if not os.path.exists(config.lora_path):
            result["errors"].append(f"LoRA path không tồn tại: {config.lora_path}")
            result["compatible"] = False
            return result
        
        # Kiểm tra adapter_config.json
        adapter_config_path = os.path.join(config.lora_path, "adapter_config.json")
        if os.path.exists(adapter_config_path):
            try:
                with open(adapter_config_path, 'r') as f:
                    adapter_config = json.load(f)
                
                # Kiểm tra base model name
                adapter_base_model = adapter_config.get("base_model_name_or_path", "")
                if adapter_base_model and adapter_base_model != config.base_model_id:
                    result["warnings"].append(
                        f"LoRA được train trên '{adapter_base_model}', "
                        f"bạn đang dùng '{config.base_model_id}'"
                    )
                
                result["info"]["adapter_config"] = adapter_config
                
            except Exception as e:
                result["warnings"].append(f"Không đọc được adapter_config.json: {e}")
        
        # Kiểm tra tokenizer files
        tokenizer_files = ["tokenizer.json", "tokenizer_config.json"]
        for file in tokenizer_files:
            file_path = os.path.join(config.lora_path, file)
            if os.path.exists(file_path):
                result["info"][f"has_{file}"] = True
            else:
                result["info"][f"has_{file}"] = False
        
        # Kiểm tra adapter weights
        adapter_weights_path = os.path.join(config.lora_path, "adapter_model.safetensors")
        if os.path.exists(adapter_weights_path):
            result["info"]["has_adapter_weights"] = True
            # Lấy size của file weights
            size_mb = os.path.getsize(adapter_weights_path) / (1024 * 1024)
            result["info"]["adapter_weights_size_mb"] = round(size_mb, 2)
        else:
            result["errors"].append("Không tìm thấy adapter_model.safetensors")
            result["compatible"] = False
        
    except Exception as e:
        result["errors"].append(f"Lỗi khi kiểm tra compatibility: {e}")
        result["compatible"] = False
    
    return result