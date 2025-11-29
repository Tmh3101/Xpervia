"""
Django management command để rebuild ma trận course-course similarity.

Sử dụng:
    python manage.py rebuild_course_similarity
    python manage.py rebuild_course_similarity --force
"""
from django.core.management.base import BaseCommand
from api.services.reco_service.cb.similarity import (
    build_and_save_course_similarity_matrix,
    load_course_similarity_matrix
)


class Command(BaseCommand):
    help = 'Rebuild course-course similarity matrix'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force rebuild even if matrix exists',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write(self.style.WARNING('REBUILD COURSE-COURSE SIMILARITY MATRIX'))
        self.stdout.write(self.style.WARNING('=' * 70))
        
        # Check if matrix already exists
        if not force:
            sim_matrix = load_course_similarity_matrix()
            if sim_matrix is not None:
                self.stdout.write(
                    self.style.SUCCESS(f'\n✅ Ma trận similarity đã tồn tại:')
                )
                self.stdout.write(f'   - Shape: {sim_matrix.shape}')
                self.stdout.write(f'   - Non-zero elements: {sim_matrix.nnz:,}')
                density = sim_matrix.nnz / (sim_matrix.shape[0] ** 2) * 100
                self.stdout.write(f'   - Density: {density:.4f}%')
                self.stdout.write(
                    self.style.WARNING('\n💡 Sử dụng --force để rebuild lại.')
                )
                return
        
        self.stdout.write('\n⏳ Đang xây dựng ma trận similarity...')
        
        try:
            import time
            start = time.time()
            
            stats = build_and_save_course_similarity_matrix()
            
            elapsed = time.time() - start
            
            self.stdout.write(self.style.SUCCESS(f'\n✅ Hoàn thành trong {elapsed:.2f}s!'))
            self.stdout.write(f'\n📊 Thống kê:')
            self.stdout.write(f'   - Số courses: {stats["n_courses"]}')
            self.stdout.write(f'   - Non-zero elements: {stats["nnz"]:,}')
            self.stdout.write(f'   - Density: {stats["density"]*100:.4f}%')
            
            # Ước tính dung lượng
            from api.services.reco_service.cb.similarity import COURSE_SIM_MATRIX_PATH
            import os
            if os.path.exists(COURSE_SIM_MATRIX_PATH):
                size_mb = os.path.getsize(COURSE_SIM_MATRIX_PATH) / (1024 * 1024)
                self.stdout.write(f'   - File size: {size_mb:.2f} MB')
            
            self.stdout.write(self.style.SUCCESS('\n✅ Ma trận đã được lưu vào artifacts!'))
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ Lỗi khi xây dựng ma trận: {str(e)}')
            )
            raise
        
        self.stdout.write(self.style.WARNING('\n' + '=' * 70))
