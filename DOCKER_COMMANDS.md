# Quick Docker Commands Reference - Xpervia

## 🚀 Khởi Động Nhanh

```bash
# 1. Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
cp chatbot_service/.env.example chatbot_service/.env

# 2. Cấu hình các file .env với thông tin Supabase

# 3. Build và khởi động
docker-compose up -d

# 4. Chạy migrations
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py seed_admin

# 5. Kiểm tra services
docker-compose ps
```

## 📦 Build & Start

```bash
# Build tất cả
docker-compose build

# Build service cụ thể
docker-compose build backend
docker-compose build frontend
docker-compose build chatbot

# Build không cache (clean build)
docker-compose build --no-cache

# Khởi động tất cả services
docker-compose up -d

# Khởi động và xem logs real-time
docker-compose up

# Khởi động service cụ thể
docker-compose up -d backend redis
```

## 🛑 Stop & Clean

```bash
# Dừng services
docker-compose stop

# Dừng và xóa containers
docker-compose down

# Xóa cả volumes (⚠️ mất data)
docker-compose down -v

# Khởi động lại
docker-compose restart

# Restart service cụ thể
docker-compose restart backend
```

## 📊 Monitoring

```bash
# Xem status
docker-compose ps

# Xem logs tất cả
docker-compose logs -f

# Logs service cụ thể
docker-compose logs -f backend
docker-compose logs -f chatbot

# Logs 100 dòng cuối
docker-compose logs --tail=100 backend

# Xem resource usage
docker stats
```

## 🔧 Truy Cập Containers

```bash
# Bash vào container
docker-compose exec backend bash
docker-compose exec chatbot bash

# Python shell
docker-compose exec backend python manage.py shell

# Django commands
docker-compose exec backend python manage.py <command>

# Redis CLI
docker-compose exec redis redis-cli
```

## 💾 Database Operations

```bash
# Migrations
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate

# Tạo superuser
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py seed_admin

# Database shell
docker-compose exec backend python manage.py dbshell

# Flush database (⚠️ xóa data)
docker-compose exec backend python manage.py flush
```

## ⚙️ Celery Operations

```bash
# Xem active tasks
docker-compose exec celery-worker celery -A backend inspect active

# Xem registered tasks
docker-compose exec celery-worker celery -A backend inspect registered

# Xem scheduled tasks
docker-compose exec celery-beat celery -A backend inspect scheduled

# Purge queue
docker-compose exec celery-worker celery -A backend purge

# Restart workers
docker-compose restart celery-worker celery-beat
```

## 🤖 Chatbot Operations

```bash
# Health check
curl http://localhost:8001/health

# Test inference
curl -X POST http://localhost:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Test question"}'

# Run evaluation
docker-compose exec chatbot python scripts/eval.py

# Rebuild RAG index
docker-compose exec chatbot python -m app.rag.indexing.build_docs
```

## 🔍 Debugging

```bash
# Xem Docker images
docker images

# Xem volumes
docker volume ls

# Inspect container
docker inspect xpervia-backend

# Xem networks
docker network ls

# Clean unused images/containers
docker system prune -a

# Xem disk usage
docker system df
```

## 📈 Scaling

```bash
# Scale workers
docker-compose up -d --scale celery-worker=4

# Scale backend (cần load balancer)
docker-compose up -d --scale backend=3
```

## 🔐 Security & Maintenance

```bash
# Update images
docker-compose pull

# Rebuild after update
docker-compose build --pull

# Xem vulnerabilities (nếu có docker scan)
docker scan xpervia-backend:latest
```

## 🌐 Access URLs

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Backend Admin: http://localhost:8000/admin
- Swagger Docs: http://localhost:8000/swagger
- Chatbot API: http://localhost:8001
- Chatbot Docs: http://localhost:8001/docs
- Redis: localhost:6379

## 🆘 Quick Fixes

### Frontend không build được
```bash
docker-compose down frontend
rm -rf frontend/.next frontend/node_modules
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### Backend database connection fail
```bash
# Kiểm tra .env
docker-compose exec backend cat .env | grep SUPABASE

# Test connection
docker-compose exec backend python manage.py check --database default
```

### Chatbot out of memory
```bash
# Restart với more memory
docker-compose down chatbot
# Edit docker-compose.yml -> increase memory limit
docker-compose up -d chatbot
```

### Redis connection issues
```bash
docker-compose restart redis
docker-compose logs redis
```

## 📝 Development Workflow

```bash
# 1. Start services
docker-compose up -d

# 2. Watch logs
docker-compose logs -f backend frontend chatbot

# 3. Make code changes (volumes auto-reload)

# 4. Test changes
curl http://localhost:8000/api/

# 5. Run tests
docker-compose exec backend python manage.py test

# 6. Commit changes
git add . && git commit -m "Your message"

# 7. Stop when done
docker-compose down
```

## 🎯 Production Commands

```bash
# Build production images
docker-compose -f docker-compose.yml build

# Start in production mode
NODE_ENV=production docker-compose up -d

# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput

# Check deployment
docker-compose exec backend python manage.py check --deploy
```

---

**Tip**: Tạo aliases trong `.bashrc` hoặc `.zshrc`:
```bash
alias dcup='docker-compose up -d'
alias dcdown='docker-compose down'
alias dclog='docker-compose logs -f'
alias dcps='docker-compose ps'
alias dcexec='docker-compose exec'
```
