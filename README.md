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
![FastAPI](https://img.shields.io/badge/FastAPI-0.117.x-009688?style=flat&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker)

# Xpervia - Hệ Thống Quản Lý Khóa Học Trực Tuyến

## 📋 Mục Lục

- [Giới Thiệu](#giới-thiệu)
- [Tính Năng Chính](#tính-năng-chính)
- [Kiến Trúc Hệ Thống](#kiến-trúc-hệ-thống)
- [Yêu Cầu Hệ Thống](#yêu-cầu-hệ-thống)
- [Cài Đặt & Chạy Dự Án](#cài-đặt--chạy-dự-án)
  - [Phương pháp 1: Docker (Khuyến nghị)](#-phương-pháp-1-docker-khuyến-nghị)
  - [Phương pháp 2: Local Development](#-phương-pháp-2-local-development)
- [Cấu Hình Chi Tiết](#cấu-hình-chi-tiết)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Đóng Góp](#đóng-góp)

---

## Giới Thiệu

**Xpervia** là nền tảng học tập trực tuyến (LMS - Learning Management System) hiện đại, giúp quản lý khóa học, học viên và giáo viên. Hệ thống hỗ trợ đăng ký khóa học, theo dõi tiến trình học tập, nộp bài tập, chấm điểm, thống kê dữ liệu và gợi ý khóa học thông minh.

## Tính Năng Chính

| Tính năng                        | Mô tả                                                                  |
| -------------------------------- | ---------------------------------------------------------------------- |
| 👤 **Quản lý người dùng**        | Đăng ký, đăng nhập, phân quyền (Admin, Giáo viên, Học viên)            |
| 📚 **Quản lý khóa học**          | Tạo, chỉnh sửa, xóa, phân loại khóa học theo danh mục                  |
| 📝 **Bài học & Bài tập**         | Nội dung học tập, video, file đính kèm, bài tập có hạn nộp             |
| ✅ **Chấm điểm & Phản hồi**      | Giáo viên chấm điểm, nhận xét bài tập học viên                         |
| 📊 **Thống kê**                  | Tiến độ học tập, số lượng khóa học, học viên đăng ký                   |
| 🎯 **Gợi ý khóa học thông minh** | Hybrid Recommendation System (Content-Based + Collaborative Filtering) |
| 🤖 **RAG Chatbot**               | Chatbot thông minh sử dụng RAG để tư vấn khóa học                      |
| ❤️ **Yêu thích khóa học**        | Lưu và quản lý danh sách khóa học yêu thích                            |

## Kiến Trúc Hệ Thống

Hệ thống Xpervia bao gồm **3 module chính**:

```
┌─────────────────────────────────────────────────────────────────┐
│                         XPERVIA SYSTEM                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   FRONTEND   │    │   BACKEND    │    │   CHATBOT    │      │
│  │  (Next.js)   │◄──►│   (Django)   │◄──►│  (FastAPI)   │      │
│  │  Port 3000   │    │  Port 8000   │    │  Port 8001   │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                             │                    │              │
│                             ▼                    │              │
│                      ┌─────────────┐             │              │
│                      │   CELERY    │             │              │
│                      │ Worker/Beat │             │              │
│                      └──────┬──────┘             │              │
│                             │                    │              │
│                      ┌──────▼──────┐             │              │
│                      │    REDIS    │◄────────────┘              │
│                      │  Port 6379  │                            │
│                      └─────────────┘                            │
│                             │                                   │
│                  ┌──────────▼──────────┐                        │
│                  │  SUPABASE (Cloud)   │                        │
│                  │  • PostgreSQL DB    │                        │
│                  │  • Authentication   │                        │
│                  │  • Storage          │                        │
│                  └─────────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

<div align="center">
    <img src="https://wvhmkaizijngdfbmpenf.supabase.co/storage/v1/object/public/xpervia-public/assets/system-structure.png" alt="System Architecture" width="600"/>
    <br/>
    <strong>Hình 1:</strong> Sơ đồ kiến trúc hệ thống
</div>

### Công Nghệ Sử Dụng

| Module               | Công nghệ                                                           |
| -------------------- | ------------------------------------------------------------------- |
| **Frontend**         | Next.js 14, React 18, TailwindCSS, ShadCN/UI, TypeScript            |
| **Backend**          | Django 5.1, Django REST Framework, Celery, Redis                    |
| **Chatbot**          | FastAPI, LangChain, HuggingFace Transformers, Sentence-Transformers |
| **Database**         | Supabase PostgreSQL, pgvector (vector search)                       |
| **Storage**          | Supabase Storage                                                    |
| **Authentication**   | Supabase Auth (JWT)                                                 |
| **Containerization** | Docker, Docker Compose                                              |

---

## Yêu Cầu Hệ Thống

### Yêu cầu chung

| Thành phần   | Yêu cầu tối thiểu                          |
| ------------ | ------------------------------------------ |
| **OS**       | Windows 10/11, macOS 10.15+, Ubuntu 20.04+ |
| **RAM**      | 8GB (16GB khuyến nghị cho Chatbot)         |
| **Disk**     | 20GB trống                                 |
| **Internet** | Kết nối ổn định (để tải models AI)         |

### Với Docker (Khuyến nghị)

- Docker Engine 20.10+
- Docker Compose 2.0+

### Với Local Development

| Module       | Yêu cầu                                |
| ------------ | -------------------------------------- |
| **Backend**  | Python 3.12+, pip                      |
| **Frontend** | Node.js 20+, npm 10+                   |
| **Chatbot**  | Python 3.12+, CUDA (optional cho GPU)  |
| **Database** | Tài khoản Supabase (free tier đủ dùng) |
| **Cache**    | Redis Server 7+                        |

---

## Cài Đặt & Chạy Dự Án

### 📁 Cấu Trúc Thư Mục

```
Xpervia/
├── backend/                 # Django REST API
│   ├── api/                 # App chính
│   │   ├── models/          # Database models
│   │   ├── views/           # API endpoints
│   │   ├── serializers/     # Data serialization
│   │   ├── services/        # Business logic
│   │   │   └── reco_service/  # Recommendation system
│   │   └── management/      # Django commands
│   ├── backend/             # Django settings
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/                # Next.js Web Application
│   ├── app/                 # Next.js App Router
│   ├── components/          # React components
│   ├── lib/                 # Utilities & API clients
│   ├── package.json
│   ├── Dockerfile
│   └── .env.example
│
├── chatbot_service/         # RAG Chatbot (FastAPI)
│   ├── app/
│   │   ├── api/             # FastAPI endpoints
│   │   ├── rag/             # RAG pipeline
│   │   │   ├── embedding/   # Text embeddings
│   │   │   ├── retrieval/   # Document retrieval
│   │   │   └── generative/  # Answer generation
│   │   └── core/            # Database & models
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── docs/                    # Documentation
├── docker-compose.yml       # Docker config
└── README.md
```

---

## 🐳 Phương pháp 1: Docker (Khuyến nghị)

### Bước 1: Clone Repository

```bash
git clone https://github.com/Tmh3101/Xpervia.git
cd Xpervia
```

### Bước 2: Tạo tài khoản Supabase

1. Truy cập [https://supabase.com](https://supabase.com) và tạo tài khoản
2. Tạo một project mới
3. Lấy các thông tin sau từ **Project Settings > API**:
   - `Project URL`
   - `anon key` (public)
   - `service_role key` (secret)
   - `JWT Secret`
4. Lấy thông tin database từ **Project Settings > Database**:
   - `Host`, `Port`, `Database name`, `User`, `Password`

### Bước 3: Cấu hình Environment Variables

#### 3.1. Backend (.env)

```bash
cp backend/.env.example backend/.env
```

Chỉnh sửa `backend/.env`:

```dotenv
# Django Settings
SECRET_KEY=your-django-secret-key-generate-one
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Supabase Configuration
SUPABASE_PROJECT_ID=your-project-id
SUPABASE_PROJECT_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret

# Supabase Database (PostgreSQL)
SUPABASE_DB_HOST=db.your-project.supabase.co
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your-db-password

# Supabase Storage Buckets
SUPABASE_STORAGE_PUBLIC_BUCKET=xpervia-public
SUPABASE_STORAGE_PRIVATE_BUCKET=xpervia-private

# Redis Configuration
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
```

#### 3.2. Frontend (.env.local)

```bash
cp frontend/.env.example frontend/.env.local
```

Chỉnh sửa `frontend/.env.local`:

```dotenv
# API URLs
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CHATBOT_API_URL=http://localhost:8001

# Supabase Client
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

#### 3.3. Chatbot Service (.env)

```bash
cp chatbot_service/.env.example chatbot_service/.env
```

Chỉnh sửa `chatbot_service/.env`:

```dotenv
# Supabase Database
SUPABASE_DB_HOST=db.your-project.supabase.co
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your-db-password

# Redis
REDIS_URL=redis://redis:6379/0

# HuggingFace Models
EMBEDDING_MODEL=Alibaba-NLP/gte-multilingual-base
EMBED_DIM=768
LLM_MODEL=arcee-ai/Arcee-VyLinh
USE_CUDA=0
```

### Bước 4: Tạo Storage Buckets trên Supabase

1. Vào **Supabase Dashboard > Storage**
2. Tạo 2 buckets:
   - `xpervia-public` (Public bucket)
   - `xpervia-private` (Private bucket)

### Bước 5: Build và Khởi động với Docker

```bash
# Build tất cả images
docker-compose build

# Khởi động tất cả services
docker-compose up -d

# Xem logs để theo dõi
docker-compose logs -f
```

### Bước 6: Khởi tạo Database và Data

```bash
# Chạy database migrations
docker-compose exec backend python manage.py migrate

# Tạo tài khoản admin mặc định (admin001@gmail.com / admin001)
docker-compose exec backend python manage.py seed_admin

# Khởi tạo hệ thống gợi ý khóa học (Recommendation System)
docker-compose exec backend python manage.py reco_init

# Build ma trận similarity cho courses
docker-compose exec backend python manage.py rebuild_course_similarity --force
```

### Bước 7: Truy cập ứng dụng

| Service                | URL                            | Mô tả                     |
| ---------------------- | ------------------------------ | ------------------------- |
| **Frontend**           | http://localhost:3000          | Giao diện web chính       |
| **Backend API**        | http://localhost:8000          | REST API                  |
| **API Docs (Swagger)** | http://localhost:8000/swagger/ | API Documentation         |
| **Chatbot API**        | http://localhost:8001          | RAG Chatbot API           |
| **Chatbot Docs**       | http://localhost:8001/docs     | Chatbot API Documentation |

### 🐳 Docker Commands Reference

```bash
# Xem trạng thái services
docker-compose ps

# Xem logs của service cụ thể
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f chatbot

# Restart một service
docker-compose restart backend

# Dừng tất cả services
docker-compose stop

# Dừng và xóa containers
docker-compose down

# Xóa cả volumes (⚠️ mất data)
docker-compose down -v

# Truy cập shell trong container
docker-compose exec backend bash
docker-compose exec frontend sh

# Chạy Django management commands
docker-compose exec backend python manage.py <command>
```

📖 **Chi tiết**: Xem [DOCKER_COMMANDS.md](./DOCKER_COMMANDS.md) để biết thêm các lệnh hữu ích.

---

## 💻 Phương pháp 2: Local Development

### Yêu cầu cài đặt trước

1. **Python 3.12+**: [Download Python](https://www.python.org/downloads/)
2. **Node.js 20+**: [Download Node.js](https://nodejs.org/)
3. **Redis Server**: [Download Redis](https://redis.io/download) hoặc dùng Docker: `docker run -d -p 6379:6379 redis:7-alpine`
4. **Git**: [Download Git](https://git-scm.com/)

### Bước 1: Clone và cấu hình

```bash
# Clone repository
git clone https://github.com/Tmh3101/Xpervia.git
cd Xpervia

# Cấu hình environment files (như hướng dẫn Docker ở trên)
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
cp chatbot_service/.env.example chatbot_service/.env
# Chỉnh sửa các file .env với thông tin Supabase của bạn
```

> **Lưu ý cho Local Development**: Thay đổi Redis URL trong các file `.env`:
>
> - `CELERY_BROKER_URL=redis://localhost:6379/0`
> - `CELERY_RESULT_BACKEND=redis://localhost:6379/1`
> - `REDIS_URL=redis://localhost:6379/0`

### Bước 2: Cài đặt và chạy Backend

```bash
cd backend

# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
venv\Scripts\activate.bat
# macOS/Linux:
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy database migrations
python manage.py migrate

# Tạo tài khoản admin
python manage.py seed_admin

# Khởi tạo Recommendation System
python manage.py reco_init
python manage.py rebuild_course_similarity --force

# Chạy development server
python manage.py runserver
```

⇒ Backend API: http://localhost:8000

### Bước 3: Chạy Celery Worker (Terminal mới)

```bash
cd backend

# Kích hoạt virtual environment
# Windows: .\venv\Scripts\Activate.ps1
# macOS/Linux: source venv/bin/activate

# Chạy Celery Worker
celery -A backend worker -l info

# (Optional) Chạy Celery Beat cho scheduled tasks (terminal khác)
celery -A backend beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Bước 4: Cài đặt và chạy Frontend

```bash
cd frontend

# Cài đặt dependencies
npm install

# Chạy development server
npm run dev
```

⇒ Frontend: http://localhost:3000

### Bước 5: Cài đặt và chạy Chatbot Service (Optional)

```bash
cd chatbot_service

# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows: .\venv\Scripts\Activate.ps1
# macOS/Linux: source venv/bin/activate

# Cài đặt dependencies (có thể mất nhiều thời gian do models AI)
pip install -r requirements.txt

# Chạy FastAPI server
uvicorn app.api.main:app --host 0.0.0.0 --port 8001 --reload
```

⇒ Chatbot API: http://localhost:8001

### Tổng hợp các terminals cần mở

| Terminal | Thư mục            | Lệnh                                            |
| -------- | ------------------ | ----------------------------------------------- |
| 1        | `backend/`         | `python manage.py runserver`                    |
| 2        | `backend/`         | `celery -A backend worker -l info`              |
| 3        | `frontend/`        | `npm run dev`                                   |
| 4        | `chatbot_service/` | `uvicorn app.api.main:app --port 8001 --reload` |
| 5        | (anywhere)         | Redis server (hoặc dùng Docker)                 |

---

<div align="center">
    <br/>
	<img src="https://wvhmkaizijngdfbmpenf.supabase.co/storage/v1/object/public/xpervia-public/assets/homepage.png" alt="Xpervia Homepage" width="700"/>
    <br/>
    <strong>Hình 2:</strong> Giao diện trang chủ website
</div>

---

## Cấu Hình Chi Tiết

### Tài khoản Admin mặc định

Sau khi chạy `seed_admin`, tài khoản admin được tạo:

| Field    | Value                |
| -------- | -------------------- |
| Email    | `admin001@gmail.com` |
| Password | `admin001`           |
| Role     | `admin`              |

> ⚠️ **Lưu ý**: Đổi mật khẩu ngay sau khi đăng nhập lần đầu!

### Các Django Management Commands

| Command                                              | Mô tả                                        |
| ---------------------------------------------------- | -------------------------------------------- |
| `python manage.py migrate`                           | Chạy database migrations                     |
| `python manage.py seed_admin`                        | Tạo tài khoản admin                          |
| `python manage.py reco_init`                         | Khởi tạo Recommendation System (TF-IDF + CF) |
| `python manage.py rebuild_course_similarity --force` | Rebuild ma trận Course Similarity            |
| `python manage.py createsuperuser`                   | Tạo superuser Django                         |

### Cấu hình Recommendation System

Hệ thống gợi ý sử dụng Hybrid Recommendation:

- **Content-Based Filtering**: TF-IDF vectors từ nội dung khóa học
- **Collaborative Filtering**: User-based CF từ hành vi enroll/favorite

Chi tiết: Xem [docs/RECOMMENDATION_SYSTEM.md](./docs/RECOMMENDATION_SYSTEM.md)

---

## API Documentation

### Backend REST API

- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/

### Chatbot API

- **FastAPI Docs**: http://localhost:8001/docs
- **Health Check**: `GET http://localhost:8001/health`
- **Ask Question**: `POST http://localhost:8001/ask`

```bash
# Ví dụ gọi Chatbot API
curl -X POST http://localhost:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Khóa học Python nào phù hợp cho người mới bắt đầu?"}'
```

---

## Troubleshooting

### Lỗi thường gặp

| Lỗi                           | Nguyên nhân        | Giải pháp                                                    |
| ----------------------------- | ------------------ | ------------------------------------------------------------ |
| `Connection refused to Redis` | Redis chưa chạy    | Khởi động Redis: `docker run -d -p 6379:6379 redis:7-alpine` |
| `Supabase connection failed`  | Sai credentials    | Kiểm tra lại file `.env`                                     |
| `Module not found`            | Thiếu dependencies | Chạy lại `pip install -r requirements.txt`                   |
| `Port already in use`         | Port đã bị chiếm   | Đổi port hoặc kill process đang dùng                         |
| `Chatbot out of memory`       | RAM không đủ       | Giảm model size hoặc tăng RAM                                |

### Reset toàn bộ dự án

```bash
# Với Docker
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d

# Local: Xóa virtual environments và cài lại
rm -rf backend/venv frontend/node_modules chatbot_service/venv
# Sau đó làm lại từ bước cài đặt
```

---

## Đóng Góp

Mọi đóng góp đều được hoan nghênh!

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

## Thay Đổi & Lịch Sử Phiên Bản

Xem chi tiết các thay đổi tại file [CHANGELOG.md](./CHANGELOG.md)

---

## 📚 Tài Liệu Tham Khảo

- [DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md) - Hướng dẫn deploy với Docker
- [DOCKER_COMMANDS.md](./DOCKER_COMMANDS.md) - Quick reference Docker commands
- [docs/RECOMMENDATION_SYSTEM.md](./docs/RECOMMENDATION_SYSTEM.md) - Chi tiết Recommendation System

## Báo Cáo Đề Tài

[📄 Xem bài báo cáo chi tiết tại đây](https://drive.google.com/file/d/1vF0H3_JqWuyNd-l0RUjkytHR8bqpEysx/view?usp=sharing)

---

<div align="center">
    <br/>
    <strong>Made with ❤️ by Xpervia Team</strong>
    <br/>
    <br/>
</div>
