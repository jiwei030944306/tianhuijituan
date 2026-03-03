"""
FastAPI应用入口
"""
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 创建FastAPI应用
app = FastAPI(
    title="智研题库云系统 API",
    description="AI驱动的试题数字化生产线",
    version="1.0.0"
)

# CORS中间件 - 必须在所有路由之前
# 安全修复：支持从环境变量配置CORS来源
cors_env = os.getenv("CORS_ORIGINS", "")
if cors_env:
    origins = [origin.strip() for origin in cors_env.split(",") if origin.strip()]
else:
    origins = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求日志中间件
from app.middleware.request_logger import RequestLoggingMiddleware
app.add_middleware(RequestLoggingMiddleware)
# 注册路由
from app.api import questions, logs, auth
from app.api.v1 import monitor

app.include_router(questions.router)
app.include_router(logs.router)
app.include_router(auth.router)
app.include_router(monitor.router, prefix="/api/v1/monitor", tags=["monitor"])
# 配置静态文件服务
# 计算项目根目录（使用绝对路径确保一致性）
# __file__ = backend/app/main.py
# .parent = backend/app/
# .parent.parent = backend/
# .parent.parent.parent = 项目根目录/
BASE_DIR = Path(__file__).resolve().parent.parent.parent
uploads_dir = BASE_DIR / "data" / "uploads"

print(f"[INFO] 上传目录路径: {uploads_dir}")

if uploads_dir.exists():
    app.mount("/static", StaticFiles(directory=str(uploads_dir)), name="static")
    print(f"[INFO] 静态文件服务已挂载: /static -> {uploads_dir}")
else:
    print(f"[WARNING] 上传目录不存在，尝试创建: {uploads_dir}")
    try:
        uploads_dir.mkdir(parents=True, exist_ok=True)
        app.mount("/static", StaticFiles(directory=str(uploads_dir)), name="static")
        print(f"[INFO] 已自动创建上传目录并挂载静态文件服务")
    except Exception as e:
        print(f"[ERROR] 创建上传目录失败: {e}")

# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "智研题库云系统 API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# 健康检查
@app.get("/health")
async def health_check():
    """
    健康检查

    返回系统状态和数据库连接池信息
    """
    from app.core.database import engine

    # 获取连接池状态
    pool_status = {
        "pool_size": engine.pool.size(),
        "checked_in": engine.pool.checkedin(),
        "checked_out": engine.pool.checkedout(),
        "overflow": engine.pool.overflow(),
        "total_connections": engine.pool.size() + engine.pool.overflow()
    }

    return {
        "status": "healthy",
        "database": {
            "connected": True,
            "pool": pool_status
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
