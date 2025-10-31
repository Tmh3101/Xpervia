import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from app.rag.hyde.hypothetical import generate_hypothetical

def main():
    query = "Khóa học lanh đạo hiệu quả bao gồm những nội dung gì?"
    result = generate_hypothetical(
        query=query,
    )

    print("===> Kết quả:", result)

    print("===> Câu trả lời giả định:")
    print(result["draft"])

if __name__ == "__main__":
    main()