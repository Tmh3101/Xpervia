<div align="center">
    <br/>
	<img src="https://wvhmkaizijngdfbmpenf.supabase.co/storage/v1/object/public/xpervia-public/assets/logo-ngang.png" alt="Xpervia Logo" width="160"/>
    <br/>
    <br/>
</div>

![React](https://img.shields.io/badge/React-18.x-61DAFB?style=flat&logo=react)
![Next.js](https://img.shields.io/badge/Next.js-14.x-000000?style=flat&logo=next.js)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.x-06B6D4?style=flat&logo=tailwind-css)
![shadcn/ui](https://img.shields.io/badge/shadcn%2Fui-latest-000000?style=flat&logo=shadcn%2Fui)
![Django](https://img.shields.io/badge/Django-5.1.x-092E20?style=flat&logo=django)
![Django REST Framework](https://img.shields.io/badge/Django_REST_Framework-3.15.x-A020F0?style=flat&logo=django-rest-framework)
![Supabase](https://img.shields.io/badge/Supabase-2.15.x-3FC084?style=flat&logo=supabase)

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

- **Backend**: Django Rest Framework, Supabase PostgreSQL, Supabase Storage, Reco Service (gợi ý khóa học)
- **Frontend**: Next.js, React, ShadCN/UI
- **Authentication**: Supabase Auth (JWT)

<div align="center">
    <img src="https://wvhmkaizijngdfbmpenf.supabase.co/storage/v1/object/public/xpervia-public/assets/system-structure.png" alt="System Architecture" width="600"/>
    
<strong>Hình 1:</strong> Sơ đồ kiến trúc hệ thống
</div>

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

&rArr; Backend server sẽ được chạy tại: _http://localhost:8000_

### Frontend

```sh
cd frontend
# Cài đặt dependencies
npm install

# Chạy ứng dụng
npm run dev
```

&rArr; Truy cập website tại đường dẫn: _http://localhost:3000_

<div align="center">
    <br/>
	<img src="https://wvhmkaizijngdfbmpenf.supabase.co/storage/v1/object/public/xpervia-public/assets/homepage.png" alt="Xpervia Homepage" width="700"/>
    <br/>
    <strong>Hình 2:</strong> </i>Giao diện trang chủ website</i>
</div>

## Đóng Góp

Mọi đóng góp đều được hoan nghênh! Hãy tạo issue hoặc gửi pull request.

## Thay Đổi & Lịch Sử Phiên Bản

Xem chi tiết các thay đổi tại file [CHANGELOG.md](./CHANGELOG.md) (bắt đầu từ version 2 dev).

---

## Báo Cáo Đề Tài

[Xem bài báo cáo chi tiết tại đây](https://drive.google.com/file/d/1vF0H3_JqWuyNd-l0RUjkytHR8bqpEysx/view?usp=sharing)
