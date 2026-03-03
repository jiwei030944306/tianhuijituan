#!/usr/bin/env python
"""
生产环境启动脚本 - 禁用热重载，提高稳定性
"""
import subprocess
import sys
import os

# 切换到backend目录
backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(backend_dir)

print(f"工作目录: {os.getcwd()}")
print("正在启动后端服务器（生产模式，无热重载）...")

# 启动uvicorn - 生产模式
try:
    subprocess.run(
        [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            # 不使用 --reload，避免频繁重载
            "--workers", "1"  # 单进程，避免资源竞争
        ],
        check=True
    )
except KeyboardInterrupt:
    print("\n服务器已停止")
except Exception as e:
    print(f"启动失败: {e}")
    sys.exit(1)