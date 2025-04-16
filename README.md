# Xpervia - Hệ Thống Quản Lý Khóa Học Trực Tuyến

## Giới Thiệu
Xpervia là nền tảng học tập trực tuyến giúp quản lý khóa học, học viên và giáo viên. Hệ thống hỗ trợ đăng ký khóa học, theo dõi tiến trình học tập, nộp bài tập, chấm điểm và thống kê dữ liệu.

## Tính Năng Chính
- **Quản lý người dùng**: Đăng ký, đăng nhập, phân quyền (Admin, Giáo viên, Học viên).
- **Quản lý khóa học**: Tạo, chỉnh sửa, xóa khóa học, phân loại khóa học.
- **Bài học & Bài tập**: Hỗ trợ nội dung học tập, video, file đính kèm, bài tập có hạn nộp.
- **Chấm điểm & Phản hồi**: Giáo viên có thể chấm điểm, nhận xét bài tập.
- **Thống kê**: Hiển thị tiến độ học tập, số lượng khóa học, học viên đăng ký.

## Công Nghệ Sử Dụng
- **Backend**: Django Rest Framework, PostgreSQL, Google Drive API.
- **Frontend**: Next.js, React, ShadCN/UI.
- **Authentication**: Token-based Authentication.

## Cài Đặt & Chạy Dự Án
### Backend
```sh
# Cài đặt môi trường ảo
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy migrations
python manage.py migrate

# Chạy server
python manage.py runserver
```

### Frontend
```sh
# Cài đặt dependencies
npm install

# Chạy ứng dụng
npm run dev
```

## Đóng Góp
Mọi đóng góp đều được hoan nghênh! Hãy tạo issue hoặc gửi pull request.
