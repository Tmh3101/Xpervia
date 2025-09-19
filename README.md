# Xpervia - Hệ Thống Quản Lý Khóa Học Trực Tuyến

## Giới Thiệu

Xpervia là nền tảng học tập trực tuyến giúp quản lý khóa học, học viên và giáo viên. Hệ thống hỗ trợ đăng ký khóa học, theo dõi tiến trình học tập, nộp bài tập, chấm điểm, thống kê dữ liệu và gợi ý khóa học thông minh (reco_service).

## Tính Năng Chính

- **Quản lý người dùng**: Đăng ký, đăng nhập, phân quyền (Admin, Giáo viên, Học viên)
- **Quản lý khóa học**: Tạo, chỉnh sửa, xóa, phân loại khóa học
- **Bài học & Bài tập**: Nội dung học tập, video, file đính kèm, bài tập có hạn nộp
- **Chấm điểm & Phản hồi**: Giáo viên chấm điểm, nhận xét bài tập
- **Thống kê**: Tiến độ học tập, số lượng khóa học, học viên đăng ký
- **Gợi ý khóa học thông minh**: Tích hợp reco_service đề xuất khóa học tương đồng

## Công Nghệ Sử Dụng

- **Backend**: Django Rest Framework, Supabase PostgreSQL, Google Drive API, Reco Service (gợi ý khóa học)
- **Frontend**: Next.js, React, ShadCN/UI
- **Authentication**: Token-based Authentication

## Cài Đặt & Chạy Dự Án

### Docker

- Dự án đã hỗ trợ Docker cho cả backend và frontend. Database sử dụng Supabase PostgreSQL (không dùng local database).
- Cấu hình kết nối Supabase trong file `.env` của backend.
- Đảm bảo đã cập nhật các file Dockerfile và docker-compose.yml phù hợp với Supabase.

### Backend

```sh
cd backend
# Cài đặt môi trường ảo
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy migrations
python manage.py migrate

# Tạo tài khoản admin mặc định
python manage.py seed_admin

# Khởi tạo hệ thống gợi ý khóa học
python manage.py reco_init

# Chạy server
python manage.py runserver
```

### Frontend

```sh
cd frontend
# Cài đặt dependencies
npm install

# Chạy ứng dụng
npm run dev
```

## Đóng Góp

Mọi đóng góp đều được hoan nghênh! Hãy tạo issue hoặc gửi pull request.

## Thay Đổi & Lịch Sử Phiên Bản

Xem chi tiết các thay đổi tại file [CHANGELOG.md](./CHANGELOG.md) (bắt đầu từ version 2 dev).
