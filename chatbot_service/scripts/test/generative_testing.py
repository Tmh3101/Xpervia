"""
Qwen2.5-0.5B-Instruct Fine-tuned RAG Generation Testing
======================================================
Test hệ thống RAG với mô hình Qwen2.5 đã fine-tuned với LoRA adapter
"""

import os
import sys
import time
from pathlib import Path

# Đảm bảo import được "app/"
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from app import config
from app.rag.generative.model import (
    build_chat_model, 
    GenerativeConfig, 
    create_model_summary,
    get_model_info
)
from app.rag.generative.answer_generation import generate_answer
from app.rag.generative.utils import (
    measure_generation_performance, 
    format_generation_log,
    validate_model_config,
    check_model_compatibility
)

def print_step(step_num, title, content=""):
    """In log từng bước một cách rõ ràng."""
    print(f"\n{'='*80}")
    print(f"📍 BƯỚC {step_num}: {title}")
    print(f"{'='*80}")
    if content:
        print(content)

def main():
    """Test Qwen2.5-0.5B-Instruct fine-tuned với RAG pipeline"""
    
    print("🚀 QWEN2.5-0.5B FINE-TUNED RAG TEST")
    print("Mục tiêu: Test mô hình Qwen đã fine-tuned với LoRA adapter trong RAG pipeline")
    print("Fine-tuned model: qwen-500m-qlora-xpervia\n")
    
    # ========================
    # BƯỚC 1: Chuẩn bị test data
    # ========================
    print_step(1, "CHUẨN BỊ TEST DATA")
    
    # Câu hỏi test đa dạng cho domain Xpervia
    test_questions = [
        "Khóa học Python cơ bản có bao nhiêu chương?",
        "Ai là giảng viên của khóa học JavaScript?", 
        "Làm thế nào để đăng ký khóa học Machine Learning?",
        "Bài tập ở chương 3 của khóa học React có khó không?",
        "Học phí khóa học AI có đắt không?",
        "Tôi có thể học trực tuyến hay phải đến lớp?",
    ]
    
    # Chunks giả lập phù hợp với domain fine-tuning
    test_chunks = [
        {
            "doc_type": "course_overview",
            "content": (
                "Khóa học Python cơ bản được thiết kế cho người mới bắt đầu lập trình, "
                "gồm 6 chương chính: 1) Giới thiệu Python và cài đặt môi trường, "
                "2) Biến và kiểu dữ liệu cơ bản, 3) Cấu trúc điều khiển và vòng lặp, "
                "4) Hàm và module trong Python, 5) Lập trình hướng đối tượng cơ bản, "
                "6) Xử lý file và ngoại lệ. Tổng thời lượng học: 25 giờ. "
                "Giảng viên: TS. Nguyễn Văn An - Chuyên gia Python với 10 năm kinh nghiệm."
            ),
            "metadata": {
                "course_overview": {
                    "course_title": "Python Cơ Bản 2024", 
                    "instructor": "TS. Nguyễn Văn An",
                    "duration": "25 hours",
                    "level": "Beginner",
                    "chapters": 6
                }
            },
        },
        {
            "doc_type": "course_overview",
            "content": (
                "Khóa học JavaScript Hiện Đại do thầy Lê Minh Hoàng giảng dạy trực tiếp. "
                "Nội dung bao gồm: ES6+, DOM manipulation, Async/Await programming, "
                "các framework phổ biến như React.js, Vue.js và Node.js backend. "
                "Yêu cầu: Có kiến thức cơ bản về HTML và CSS. "
                "Học phí: 1.800.000 VNĐ (có giảm giá 30% cho sinh viên)."
            ),
            "metadata": {
                "course_overview": {
                    "course_title": "JavaScript Hiện Đại",
                    "instructor": "Lê Minh Hoàng", 
                    "prerequisites": "HTML, CSS cơ bản",
                    "price": "1,800,000 VNĐ",
                    "discount": "30% cho sinh viên"
                }
            },
        },
        {
            "doc_type": "lesson",
            "content": (
                "Chương 3: React Hooks và State Management trong JavaScript Hiện Đại. "
                "Bài tập thực hành: Xây dựng ứng dụng Todo App hoàn chỉnh sử dụng useState và useEffect. "
                "Độ khó: Trung bình (cần nắm vững React cơ bản). "
                "Thời gian hoàn thành: 4-6 giờ làm bài và debug. "
                "Yêu cầu: Học viên cần hoàn thành ít nhất 80% bài tập để được chấm điểm qua chương."
            ),
            "metadata": {
                "lesson": {
                    "lesson_title": "React Hooks và State Management",
                    "course_title": "JavaScript Hiện Đại",
                    "chapter_number": 3,
                    "difficulty": "Medium",
                    "estimated_time": "4-6 hours"
                }
            },
        },
        {
            "doc_type": "course_detail", 
            "content": (
                "Quy trình đăng ký khóa học Machine Learning Advanced tại Xpervia: "
                "Bước 1: Đăng nhập hoặc tạo tài khoản trên hệ thống Xpervia.edu.vn. "
                "Bước 2: Chọn khóa học 'ML Advanced' trong danh mục AI/Data Science. "
                "Bước 3: Thanh toán học phí qua VNPay, chuyển khoản ngân hàng hoặc trả góp. "
                "Bước 4: Chờ xác nhận từ phòng đào tạo và nhận link tham gia lớp học online. "
                "Học phí: 2.500.000 VNĐ (giảm 20% cho sinh viên, giảm 15% nếu đăng ký nhóm 3+ người)."
            ),
            "metadata": {
                "course_overview": {
                    "course_title": "Machine Learning Advanced",
                    "price": "2,500,000 VNĐ",
                    "student_discount": "20%",
                    "group_discount": "15% (3+ người)",
                    "registration_platform": "Xpervia.edu.vn"
                }
            },
        },
        {
            "doc_type": "course_overview",
            "content": (
                "Khóa học Artificial Intelligence (AI) Fundamentals - Khóa học AI toàn diện nhất tại Việt Nam. "
                "Học phí: 3.200.000 VNĐ cho khóa cơ bản, 4.800.000 VNĐ cho khóa nâng cao. "
                "Hình thức: 100% trực tuyến với live session mỗi tuần, có bài tập thực hành với dataset thực tế. "
                "Chứng chỉ: Được cấp chứng chỉ AI Professional sau khi hoàn thành và vượt qua final project."
            ),
            "metadata": {
                "course_overview": {
                    "course_title": "AI Fundamentals",
                    "price_basic": "3,200,000 VNĐ",
                    "price_advanced": "4,800,000 VNĐ", 
                    "format": "100% Online",
                    "certificate": "AI Professional"
                }
            },
        }
    ]
    
    # Lịch sử hội thoại mẫu theo context Xpervia
    test_history = [
        {"role": "user", "content": "Xin chào, tôi muốn tìm hiểu về các khóa học lập trình tại Xpervia."},
        {"role": "assistant", "content": "Chào bạn! Xpervia cung cấp đa dạng khóa học lập trình từ cơ bản đến nâng cao như Python, JavaScript, Machine Learning và AI. Tất cả đều có giảng viên kinh nghiệm và hỗ trợ học tập 24/7. Bạn quan tâm đến lĩnh vực nào cụ thể?"},
        {"role": "user", "content": "Tôi là người mới bắt đầu, muốn học Python để làm data science sau này."},
        {"role": "assistant", "content": "Rất tuyệt! Tôi khuyến nghị bạn bắt đầu với khóa 'Python Cơ Bản 2024' của TS. Nguyễn Văn An. Khóa học này được thiết kế đặc biệt cho người mới, có 6 chương từ cơ bản đến nâng cao. Sau đó bạn có thể tiếp tục với khóa Machine Learning Advanced."},
    ]
    
    print(f"📋 Prepared {len(test_questions)} test questions")
    print(f"📦 Prepared {len(test_chunks)} context chunks")  
    print(f"💬 Prepared conversation history with {len(test_history)} exchanges")
    
    # ========================
    # BƯỚC 2: Cấu hình Qwen fine-tuned model
    # ========================
    print_step(2, "CẤU HÌNH QWEN FINE-TUNED MODEL")
    
    # Cấu hình cho fine-tuned model
    model_config = GenerativeConfig(
        base_model_id="Qwen/Qwen2.5-0.5B-Instruct",
        lora_path="model/qwen-500m-qlora-xpervia/final",
        device="cpu",  # Có thể chuyển sang "cuda" nếu có GPU
        dtype="float32",  # float32 cho CPU, float16 cho GPU
        load_in_4bit=False,  # False cho CPU, True cho GPU để tiết kiệm VRAM
        merge_adapters=False,  # Giữ linh hoạt
        gen_kwargs={
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9,
            "repetition_penalty": 1.1,
            "max_new_tokens": 512,
            "pad_token_id": None,  # Sẽ được set tự động
        }
    )
    
    # Validate config
    validation_errors = validate_model_config(model_config)
    if validation_errors:
        print("⚠️  Configuration Warnings:")
        for error in validation_errors:
            print(f"   - {error}")
    else:
        print("✅ Model configuration is valid")
    
    # Kiểm tra compatibility
    compat_check = check_model_compatibility(model_config)
    print(f"\n🔍 Model Compatibility Check:")
    print(f"   Compatible: {'✅' if compat_check['compatible'] else '❌'}")
    
    if compat_check["warnings"]:
        print("   Warnings:")
        for warning in compat_check["warnings"]:
            print(f"   - ⚠️ {warning}")
    
    if compat_check["errors"]:
        print("   Errors:")
        for error in compat_check["errors"]:
            print(f"   - ❌ {error}")
        print("\n💥 Cannot continue due to compatibility errors!")
        return
    
    # In thông tin model
    model_info = get_model_info(model_config)
    print(f"\n📊 Model Information:")
    print(f"   Base Model: {model_config.base_model_id}")
    print(f"   LoRA Path: {model_config.lora_path}")
    print(f"   LoRA Exists: {'✅' if model_info.get('lora_path_exists') else '❌'}")
    print(f"   Device: {model_config.device}")
    print(f"   4-bit Quantization: {model_config.load_in_4bit}")
    print(f"   Generation params: {model_config.gen_kwargs}")

    # ========================
    # BƯỚC 3: Load fine-tuned model
    # ========================  
    print_step(3, "LOAD FINE-TUNED QWEN MODEL")
    
    def load_model():
        print("⏳ Loading Qwen2.5-0.5B fine-tuned model with LoRA adapter...")
        return build_chat_model(model_config)
    
    # Đo performance của việc load model
    load_metrics = measure_generation_performance(load_model)
    
    if not load_metrics["success"]:
        print(f"❌ Model loading failed: {load_metrics['error']}")
        return
    
    chat_model = load_metrics["result"]
    print(f"✅ Fine-tuned model loaded successfully!")
    print(f"   Duration: {load_metrics['duration_seconds']}s")
    print(f"   Memory used: {load_metrics['memory_delta_mb']:.1f} MB")
    
    # ========================
    # BƯỚC 4: Test generation scenarios
    # ========================
    print_step(4, "TEST GENERATION SCENARIOS")
    
    scenarios = [
        {
            "name": "Simple Q&A về Python Course",
            "question": test_questions[0],
            "chunks": test_chunks[:1],
            "history": None,
            "use_simple_prompt": False
        },
        {
            "name": "Q&A về Instructor với Full Context", 
            "question": test_questions[1],
            "chunks": test_chunks[:2],
            "history": None,
            "use_simple_prompt": False
        },
        {
            "name": "Conversational với History",
            "question": test_questions[0], 
            "chunks": test_chunks[:1],
            "history": test_history,
            "use_simple_prompt": False
        },
        {
            "name": "Registration Process (Complex)",
            "question": test_questions[2],
            "chunks": test_chunks[2:4],
            "history": None,
            "use_simple_prompt": False
        },
        {
            "name": "Pricing Question",
            "question": test_questions[4],
            "chunks": test_chunks[3:5],
            "history": None,
            "use_simple_prompt": False
        },
        {
            "name": "Learning Format Question",
            "question": test_questions[5],
            "chunks": test_chunks[4:5],
            "history": None,
            "use_simple_prompt": True  # Test fallback
        },
    ]
    
    results = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🧪 Test Scenario {i}: {scenario['name']}")
        print(f"   Question: {scenario['question'][:60]}...")
        print(f"   Chunks: {len(scenario['chunks'])}")
        print(f"   History: {'Yes' if scenario['history'] else 'No'}")
        print(f"   Simple prompt: {scenario['use_simple_prompt']}")
        
        # Định nghĩa generation function cho scenario này
        def generate_for_scenario():
            return generate_answer(
                chat=chat_model,
                question=scenario["question"],
                retrieved_chunks=scenario["chunks"],
                history=scenario["history"],
                use_simple_prompt=scenario["use_simple_prompt"]
            )
        
        # Đo performance
        gen_metrics = measure_generation_performance(generate_for_scenario)
        
        if gen_metrics["success"]:
            answer = gen_metrics["result"]
            print(f"   ✅ Success in {gen_metrics['duration_seconds']}s")
            print(f"   📝 Answer ({len(answer)} chars, ~{len(answer.split())} words):")
            print(f"      {answer}")
            
            # Log chi tiết
            detailed_log = format_generation_log(
                question=scenario["question"],
                context_length=sum(len(chunk["content"]) for chunk in scenario["chunks"]),
                answer=answer,
                duration=gen_metrics["duration_seconds"],
                model_config=model_config
            )
            print(f"   📊 Performance:")
            for line in detailed_log.split('\n'):
                if line.strip():
                    print(f"      {line}")
            
        else:
            print(f"   ❌ Failed: {gen_metrics['error']}")
            answer = None
        
        # Lưu kết quả
        results.append({
            "scenario": scenario["name"],
            "question": scenario["question"],
            "success": gen_metrics["success"],
            "answer": answer,
            "metrics": gen_metrics
        })
        
        # Nghỉ giữa các test để tránh overload
        time.sleep(1)
    
    # ========================
    # BƯỚC 5: Tổng kết và đánh giá
    # ========================
    print_step(5, "TỔNG KẾT VÀ ĐÁNH GIÁ KẾT QUẢ")
    
    successful_tests = sum(1 for r in results if r["success"])
    total_tests = len(results)
    
    print(f"📊 Test Summary:")
    print(f"   Total tests: {total_tests}")
    print(f"   Successful: {successful_tests}")
    print(f"   Failed: {total_tests - successful_tests}")
    print(f"   Success rate: {successful_tests/total_tests*100:.1f}%")
    
    if successful_tests > 0:
        successful_results = [r for r in results if r["success"]]
        avg_duration = sum(r["metrics"]["duration_seconds"] for r in successful_results) / len(successful_results)
        avg_answer_length = sum(len(r["answer"]) for r in successful_results) / len(successful_results)
        avg_words = sum(len(r["answer"].split()) for r in successful_results) / len(successful_results)
        
        print(f"\n📈 Performance Metrics:")
        print(f"   Average duration: {avg_duration:.2f}s") 
        print(f"   Average answer length: {avg_answer_length:.0f} chars")
        print(f"   Average words per answer: {avg_words:.0f} words")
        print(f"   Average speed: {avg_words/avg_duration:.1f} words/sec")
        
        # Memory metrics từ model loading
        print(f"   Model loading time: {load_metrics['duration_seconds']:.2f}s")
        print(f"   Model memory footprint: {load_metrics['memory_delta_mb']:.1f} MB")
    
    print(f"\n📝 Individual Results:")
    for i, result in enumerate(results, 1):
        status = "✅" if result["success"] else "❌"
        duration = result["metrics"]["duration_seconds"]
        print(f"\n   {i}. {status} {result['scenario']} ({duration:.2f}s)")
        print(f"      Q: {result['question']}")
        
        if result["success"] and result["answer"]:
            # Hiển thị answer với word wrapping
            answer_lines = []
            words = result["answer"].split()
            current_line = ""
            for word in words:
                if len(current_line + " " + word) <= 70:
                    current_line += " " + word if current_line else word
                else:
                    if current_line:
                        answer_lines.append(current_line)
                    current_line = word
            if current_line:
                answer_lines.append(current_line)
            
            print(f"      A: {answer_lines[0] if answer_lines else ''}")
            for line in answer_lines[1:]:
                print(f"         {line}")
    
    # Đánh giá chất lượng (manual assessment)
    print(f"\n🎯 Quality Assessment:")
    quality_score = 0
    
    # Kiểm tra các tiêu chí chất lượng
    if successful_tests == total_tests:
        quality_score += 30  # Tất cả test pass
        print("   ✅ All tests passed (+30 points)")
    elif successful_tests > total_tests * 0.8:
        quality_score += 20  # >80% pass
        print(f"   ✅ High success rate: {successful_tests}/{total_tests} (+20 points)")
    
    if successful_tests > 0:
        # Kiểm tra độ dài câu trả lời hợp lý
        avg_length = sum(len(r["answer"]) for r in results if r["success"]) / successful_tests
        if 50 <= avg_length <= 500:
            quality_score += 20
            print("   ✅ Answer length appropriate (+20 points)")
        
        # Kiểm tra tốc độ generation
        avg_speed = sum(len(r["answer"].split()) / r["metrics"]["duration_seconds"] 
                       for r in results if r["success"] and r["metrics"]["duration_seconds"] > 0) / successful_tests
        if avg_speed >= 10:  # >= 10 words/sec
            quality_score += 20
            print(f"   ✅ Good generation speed: {avg_speed:.1f} words/sec (+20 points)")
        
        # Kiểm tra memory usage hợp lý
        if load_metrics["memory_delta_mb"] < 2000:  # < 2GB
            quality_score += 15
            print(f"   ✅ Reasonable memory usage: {load_metrics['memory_delta_mb']:.1f} MB (+15 points)")
        
        # Kiểm tra có câu trả lời bằng tiếng Việt
        vietnamese_answers = sum(1 for r in results if r["success"] and any(
            char in r["answer"] for char in "àáảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ"
        ))
        if vietnamese_answers > 0:
            quality_score += 15
            print(f"   ✅ Vietnamese language support: {vietnamese_answers} answers (+15 points)")
    
    print(f"\n🏆 Overall Quality Score: {quality_score}/100")
    
    # Final verdict
    if quality_score >= 80:
        print(f"\n🎉 EXCELLENT! Qwen fine-tuned model hoạt động rất tốt trong RAG pipeline!")
        print("   Model đã sẵn sàng để deploy vào production.")
    elif quality_score >= 60:
        print(f"\n👍 GOOD! Qwen fine-tuned model hoạt động ổn định.")
        print("   Có thể cần fine-tune thêm một vài hyperparameters để tối ưu hơn.")
    elif quality_score >= 40:
        print(f"\n⚠️  FAIR! Model hoạt động nhưng cần cải thiện.")
        print("   Nên kiểm tra lại data training hoặc tăng số epoch fine-tuning.")
    else:
        print(f"\n💥 POOR! Model cần được fine-tune lại hoặc kiểm tra configuration.")
    
    return results

if __name__ == "__main__":
    try:
        results = main()
        print(f"\n📋 Test completed with {len(results)} scenarios tested.")
        print("Cảm ơn bạn đã sử dụng Xpervia RAG Testing Suite! 🚀")
        
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        
    except Exception as e:
        print(f"\n💥 Test crashed with error: {e}")
        import traceback
        traceback.print_exc()
        print("\n🔧 Debug suggestions:")
        print("   1. Kiểm tra đường dẫn LoRA adapter")
        print("   2. Kiểm tra dependencies (transformers, peft, torch)")
        print("   3. Kiểm tra memory available")
        print("   4. Thử chuyển sang CPU nếu đang dùng GPU")