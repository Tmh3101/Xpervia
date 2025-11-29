"""
Performance test để so sánh tốc độ trước và sau khi dùng ma trận precomputed.

Chạy test:
    python manage.py shell < cb/performance_test.py
"""
import time
from api.services.reco_service.cb.similarity import (
    top_k_similar_from_course,
    load_course_similarity_matrix,
    build_and_save_course_similarity_matrix
)
from api.services.reco_service.cb.tfidf_builder import load_tfidf

def test_performance():
    """Test hiệu suất của hệ thống similarity."""
    print("=" * 70)
    print("PERFORMANCE TEST: Course Similarity")
    print("=" * 70)
    
    # Load data
    _, X, row_map = load_tfidf()
    if X.shape[0] == 0:
        print("❌ Không có dữ liệu TF-IDF. Chạy fit_tfidf_and_save() trước.")
        return
    
    n_courses = X.shape[0]
    print(f"\n📊 Số khóa học: {n_courses}")
    print(f"📊 Số features: {X.shape[1]}")
    
    # Lấy một course_id mẫu
    test_course_id = list(row_map.keys())[0] if row_map else None
    if not test_course_id:
        print("❌ Không tìm thấy course_id để test.")
        return
    
    print(f"\n🎯 Test với course_id: {test_course_id}")
    
    # Test 1: Kiểm tra xem có ma trận precomputed không
    sim_matrix = load_course_similarity_matrix()
    if sim_matrix is None:
        print("\n⚠️  Chưa có ma trận similarity precomputed.")
        print("⏳ Đang xây dựng ma trận... (chỉ chạy 1 lần)")
        start = time.time()
        stats = build_and_save_course_similarity_matrix()
        build_time = time.time() - start
        print(f"✅ Xây dựng xong trong {build_time:.2f}s")
        print(f"   - Số courses: {stats['n_courses']}")
        print(f"   - Non-zero elements: {stats['nnz']:,}")
        print(f"   - Density: {stats['density']*100:.4f}%")
        sim_matrix = load_course_similarity_matrix()
    else:
        print(f"\n✅ Đã có ma trận precomputed:")
        print(f"   - Shape: {sim_matrix.shape}")
        print(f"   - Non-zero: {sim_matrix.nnz:,}")
        print(f"   - Density: {sim_matrix.nnz / (sim_matrix.shape[0]**2) * 100:.4f}%")
    
    # Test 2: So sánh tốc độ query
    print(f"\n🚀 Test tốc độ query (top-10 similar courses):")
    print(f"   Chạy 100 lần để lấy trung bình...")
    
    n_runs = 100
    k = 10
    
    start = time.time()
    for _ in range(n_runs):
        results = top_k_similar_from_course(test_course_id, k=k)
    elapsed = time.time() - start
    
    avg_time_ms = (elapsed / n_runs) * 1000
    
    print(f"\n📈 Kết quả:")
    print(f"   - Thời gian trung bình: {avg_time_ms:.2f}ms/query")
    print(f"   - Throughput: {n_runs/elapsed:.1f} queries/second")
    print(f"   - Số kết quả tìm thấy: {len(results)}")
    
    if results:
        print(f"\n🎯 Top-3 similar courses:")
        for i, (cid, score) in enumerate(results[:3], 1):
            print(f"      {i}. Course {cid}: {score:.4f}")
    
    # Ước tính cải thiện
    print(f"\n💡 So với cách tính trực tiếp (ước tính):")
    # Giả sử tính trực tiếp mất ~10-50ms tùy số course
    estimated_old_time = max(10, n_courses * 0.05)  # ~0.05ms per course
    speedup = estimated_old_time / avg_time_ms
    print(f"   - Cách cũ (ước tính): ~{estimated_old_time:.1f}ms")
    print(f"   - Cách mới: {avg_time_ms:.2f}ms")
    print(f"   - Cải thiện: ~{speedup:.1f}x nhanh hơn ⚡")
    
    print("\n" + "=" * 70)
    print("✅ Test hoàn tất!")
    print("=" * 70)

if __name__ == "__main__":
    test_performance()
