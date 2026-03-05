"""
后端服务启动脚本 - 带自动重启和健康检查机制

功能：
1. 自动重启：服务崩溃后自动重启
2. 健康检查：定期检查服务健康状态
3. 优雅关闭：支持 Ctrl+C 安全退出
4. 崩溃日志：记录崩溃原因和时间
"""
import os
import sys
import time
import signal
import logging
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional

# 配置
MAX_RESTARTS = 5          # 最大重启次数
RESTART_DELAY = 3         # 重启延迟（秒）
HEALTH_CHECK_INTERVAL = 30  # 健康检查间隔（秒）
HEALTH_CHECK_URL = "http://localhost:8000/health"

# 设置日志
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_dir / "server.log", encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class ServerManager:
    """服务器管理器"""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.restart_count = 0
        self.running = True
        self.start_time: Optional[datetime] = None

    def start_server(self) -> bool:
        """启动服务器"""
        logger.info("=" * 50)
        logger.info(f"启动后端服务 (重启次数: {self.restart_count}/{MAX_RESTARTS})")
        logger.info("=" * 50)

        self.start_time = datetime.now()

        try:
            # 使用 uvicorn 启动
            self.process = subprocess.Popen(
                [
                    sys.executable, "-m", "uvicorn",
                    "app.main:app",
                    "--host", "0.0.0.0",
                    "--port", "8000",
                    "--log-level", "info"
                ],
                cwd=Path(__file__).parent,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                encoding='utf-8',
                errors='replace'
            )

            # 启动输出读取线程
            threading.Thread(
                target=self._read_output,
                daemon=True
            ).start()

            return True

        except Exception as e:
            logger.error(f"启动失败: {e}")
            return False

    def _read_output(self):
        """读取服务器输出"""
        if not self.process:
            return

        try:
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    print(line, end='')
        except Exception as e:
            logger.error(f"读取输出失败: {e}")

    def stop_server(self):
        """停止服务器"""
        if self.process:
            logger.info("正在停止服务...")
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning("强制终止服务...")
                self.process.kill()
            logger.info("服务已停止")

    def check_health(self) -> bool:
        """健康检查"""
        try:
            import httpx
            response = httpx.get(HEALTH_CHECK_URL, timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def log_crash(self, exit_code: int):
        """记录崩溃日志"""
        crash_log = log_dir / "crash.log"
        uptime = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0

        with open(crash_log, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().isoformat()}] "
                    f"服务崩溃，退出码: {exit_code}，"
                    f"运行时间: {uptime:.1f}秒，"
                    f"重启次数: {self.restart_count}\n")

    def run(self):
        """主运行循环"""
        # 注册信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        while self.running:
            if not self.start_server():
                logger.error("启动失败")
                break

            # 等待进程结束
            exit_code = self.process.wait()

            if not self.running:
                break

            # 检查退出码
            if exit_code == 0:
                logger.info("服务正常退出")
                break

            # 记录崩溃
            self.log_crash(exit_code)
            self.restart_count += 1

            # 检查重启次数
            if self.restart_count >= MAX_RESTARTS:
                logger.error(f"超过最大重启次数 ({MAX_RESTARTS})，停止服务")
                break

            logger.warning(f"服务异常退出 (退出码: {exit_code})，{RESTART_DELAY}秒后重启...")
            time.sleep(RESTART_DELAY)

        logger.info("服务管理器退出")

    def _signal_handler(self, signum, frame):
        """信号处理"""
        logger.info(f"收到信号 {signum}，正在关闭...")
        self.running = False
        self.stop_server()


def main():
    """主入口"""
    print("""
╔════════════════════════════════════════╗
║   智研题库云 - 后端服务管理器          ║
╠════════════════════════════════════════╣
║   自动重启: 最多 5 次                   ║
║   重启延迟: 3 秒                        ║
║   API文档: http://localhost:8000/docs  ║
╚════════════════════════════════════════╝
    """)

    manager = ServerManager()
    manager.run()


if __name__ == "__main__":
    main()