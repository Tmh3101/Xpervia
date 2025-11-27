# Docker Deployment Guide - Xpervia

## Tổng Quan

Hệ thống Xpervia bao gồm 6 services chính được containerized:

1. **backend** - Django REST API (port 8000)
2. **frontend** - Next.js web application (port 3000)
3. **chatbot** - RAG Chatbot Service với FastAPI (port 8001)
4. **redis** - Cache và message broker (port 6379)
5. **celery-worker** - Xử lý background tasks
6. **celery-beat** - Scheduled tasks scheduler

## Cấu Trúc Thư Mục

```
Xpervia/
├── backend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── .env.example
│   └── package.json
├── chatbot_service/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── .env.example
│   └── requirements.txt
└── docker-compose.yml
```

## Yêu Cầu Hệ Thống

- Docker Engine 20.10+
- Docker Compose 2.0+
- 8GB RAM (tối thiểu cho chatbot service)
- 20GB ổ cứng trống
- Kết nối Internet (để tải models từ HuggingFace)

## Cài Đặt & Cấu Hình

### Bước 1: Chuẩn Bị Environment Variables

Tạo file `.env` cho mỗi module dựa trên file `.env.example`:

#### Backend
```bash
cd backend
cp .env.example .env
# Chỉnh sửa .env với thông tin Supabase của bạn
```

#### Frontend
```bash
cd frontend
cp .env.example .env.local
# Cập nhật API URLs
```

#### Chatbot Service
```bash
cd chatbot_service
cp .env.example .env
# Cấu hình database và model paths
```

### Bước 2: Build Images

```bash
# Build tất cả services
docker-compose build

# Hoặc build từng service riêng lẻ
docker-compose build backend
docker-compose build frontend
docker-compose build chatbot
```

### Bước 3: Khởi Chạy Services

```bash
# Chạy tất cả services
docker-compose up -d

# Xem logs
docker-compose logs -f

# Chỉ chạy một số services
docker-compose up -d backend redis
```

### Bước 4: Khởi Tạo Database

```bash
# Chạy migrations
docker-compose exec backend python manage.py migrate

# Tạo superuser
docker-compose exec backend python manage.py seed_admin

# Khởi tạo recommendation system
docker-compose exec backend python manage.py reco_init
```

### Bước 5: Khởi Tạo Chatbot Service

```bash
# Build RAG documents (nếu cần)
docker-compose exec chatbot python -m app.rag.indexing.build_docs

# Test chatbot service
curl http://localhost:8001/health
```

## Các Lệnh Thường Dùng

### Quản Lý Services

```bash
# Dừng tất cả services
docker-compose stop

# Khởi động lại
docker-compose restart

# Xóa containers (giữ volumes)
docker-compose down

# Xóa containers và volumes
docker-compose down -v

# Xem trạng thái
docker-compose ps
```

### Xem Logs

```bash
# Logs của tất cả services
docker-compose logs -f

# Logs của service cụ thể
docker-compose logs -f backend
docker-compose logs -f chatbot

# Xem logs 100 dòng cuối
docker-compose logs --tail=100 backend
```

### Truy Cập Container

```bash
# Bash vào backend container
docker-compose exec backend bash

# Python shell trong backend
docker-compose exec backend python manage.py shell

# Chạy lệnh trong chatbot
docker-compose exec chatbot python scripts/eval.py
```

### Database Management

```bash
# Tạo migrations
docker-compose exec backend python manage.py makemigrations

# Chạy migrations
docker-compose exec backend python manage.py migrate

# Backup database (từ Supabase)
# Sử dụng Supabase dashboard hoặc pg_dump

# Load data fixtures
docker-compose exec backend python manage.py loaddata fixtures/data.json
```

### Celery Tasks

```bash
# Xem Celery workers
docker-compose exec celery-worker celery -A backend inspect active

# Xem scheduled tasks
docker-compose exec celery-beat celery -A backend inspect scheduled

# Purge queue
docker-compose exec celery-worker celery -A backend purge
```

## Production Deployment

### Optimization cho Production

1. **Backend Dockerfile** đã được tối ưu với:
   - Multi-stage build để giảm image size
   - Gunicorn với 4 workers
   - Health checks
   - Non-root user (có thể thêm nếu cần)

2. **Frontend Dockerfile** sử dụng:
   - Standalone output mode
   - Multi-stage build
   - Non-root user (nextjs)
   - Optimized production build

3. **Chatbot Dockerfile** bao gồm:
   - Cache HuggingFace models trong volume
   - Optimized torch và transformers
   - Health checks

### Environment Variables cho Production

```bash
# Backend
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
SECRET_KEY=<generate-strong-random-key>

# Frontend
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### Scaling Services

```bash
# Scale celery workers
docker-compose up -d --scale celery-worker=4

# Scale backend (với load balancer)
docker-compose up -d --scale backend=3
```

### Monitoring & Health Checks

Services đã có health checks tích hợp:
- Backend: `http://localhost:8000/api/`
- Frontend: `http://localhost:3000/`
- Chatbot: `http://localhost:8001/health`
- Redis: `redis-cli ping`

## Troubleshooting

### Chatbot Service Out of Memory

```bash
# Tăng memory limit trong docker-compose.yml
services:
  chatbot:
    deploy:
      resources:
        limits:
          memory: 8G
```

### Frontend Build Fails

```bash
# Clear node_modules và rebuild
docker-compose down frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### Database Connection Issues

```bash
# Kiểm tra connection string
docker-compose exec backend python -c "from django.conf import settings; print(settings.DATABASES)"

# Test PostgreSQL connection
docker-compose exec backend python manage.py dbshell
```

### Redis Connection Issues

```bash
# Kiểm tra Redis
docker-compose exec redis redis-cli ping

# Xem Redis logs
docker-compose logs redis
```

## GPU Support (Optional)

Để sử dụng GPU cho chatbot service:

1. Cài đặt NVIDIA Container Toolkit
2. Uncomment GPU config trong `docker-compose.yml`:

```yaml
chatbot:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

3. Set `USE_CUDA=1` trong chatbot `.env`

## Backup & Recovery

### Volumes

```bash
# Backup Redis data
docker run --rm -v xpervia_redis_data:/data -v $(pwd):/backup alpine tar czf /backup/redis_backup.tar.gz -C /data .

# Backup HuggingFace cache
docker run --rm -v xpervia_chatbot_cache:/cache -v $(pwd):/backup alpine tar czf /backup/hf_cache_backup.tar.gz -C /cache .
```

### Database

Database được host trên Supabase, sử dụng Supabase dashboard để backup/restore.

## Performance Tips

1. **Pre-download models**: Tải models về trước để giảm thời gian khởi động:
```bash
docker-compose run --rm chatbot python -c "from transformers import AutoModel; AutoModel.from_pretrained('Alibaba-NLP/gte-multilingual-base')"
```

2. **Use volume mounts**: Sử dụng named volumes cho cache:
   - `chatbot_cache` cho HuggingFace models
   - `redis_data` cho persistence

3. **Optimize workers**: Điều chỉnh số workers phù hợp với CPU:
```yaml
backend:
  command: gunicorn --workers $((2 * $(nproc) + 1)) ...
```

## Security Checklist

- [ ] Thay đổi tất cả default secrets/keys
- [ ] Sử dụng strong passwords cho database
- [ ] Giới hạn ALLOWED_HOSTS và CORS_ALLOWED_ORIGINS
- [ ] Enable SSL/TLS cho production
- [ ] Sử dụng secrets management (Docker secrets, Vault)
- [ ] Regular security updates cho base images
- [ ] Không commit file `.env` vào git

## Support & Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [Next.js Docker Deployment](https://nextjs.org/docs/deployment#docker-image)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Supabase Documentation](https://supabase.com/docs)

---

**Lưu ý**: File này mô tả deployment với Docker Compose cho development và staging. Để production deployment trên cloud (AWS, GCP, Azure), cân nhắc sử dụng Kubernetes hoặc managed container services.
