#!/usr/bin/env python
"""
后端服务器启动脚本
"""
import subprocess
import sys
import os

# 切换到backend目录
backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(backend_dir)

print(f"工作目录: {os.getcwd()}")
print("正在启动后端服务器...")

# 启动uvicorn
try:
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        check=True
    )
except KeyboardInterrupt:
    print("\n服务器已停止")
except Exception as e:
    print(f"启动失败: {e}")
    sys.exit(1)