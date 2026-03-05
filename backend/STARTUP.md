# 后端服务启动方式

## 方式一：简单启动（开发环境）

```bash
# 使用 uvicorn 热重载（修改代码自动重启）
python start.py
# 或
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**特点**：代码修改后自动重载，适合开发调试

---

## 方式二：带重启机制启动（推荐）

```bash
# 批处理脚本（Windows）
start_with_restart.bat

# Python 脚本（跨平台）
python start_server.py
```

**特点**：
- 服务崩溃后自动重启
- 最多重启 5 次
- 记录崩溃日志到 `logs/crash.log`
- 支持 Ctrl+C 安全退出

---

## 方式三：生产环境部署

### 使用 Gunicorn（Linux/Mac）

```bash
pip install gunicorn

gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --keep-alive 5 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log
```

### 使用 PM2（推荐）

```bash
# 安装 PM2
npm install -g pm2

# 启动服务
pm2 start "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000" --name zhiyan-backend

# 查看状态
pm2 status

# 查看日志
pm2 logs zhiyan-backend

# 重启服务
pm2 restart zhiyan-backend

# 停止服务
pm2 stop zhiyan-backend

# 开机自启
pm2 startup
pm2 save
```

### 使用 Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t zhiyan-backend .
docker run -d -p 8000:8000 --restart always zhiyan-backend
```

---

## 重启机制对比

| 方式 | 热重载 | 崩溃重启 | 日志记录 | 适用场景 |
|------|--------|----------|----------|----------|
| `start.py` | ✅ | ❌ | ❌ | 开发调试 |
| `start_server.py` | ❌ | ✅ (5次) | ✅ | 测试/生产 |
| `start_with_restart.bat` | ❌ | ✅ (5次) | ✅ | Windows |
| PM2 | ❌ | ✅ (无限) | ✅ | 生产环境 |
| Docker | ❌ | ✅ (无限) | ✅ | 生产环境 |