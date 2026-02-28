import os
import sys
import subprocess

backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(backend_dir)

print(f"工作目录: {os.getcwd()}")
print("启动后端服务器...")
print("按 Ctrl+C 停止服务器\n")

try:
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        check=False
    )
except KeyboardInterrupt:
    print("\n\n服务器已停止")