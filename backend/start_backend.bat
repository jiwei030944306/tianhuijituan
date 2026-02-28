@echo off
chcp 65001 >nul
echo ========================================
echo   智研题库云 - 后端服务启动
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.11+
    pause
    exit /b 1
)

echo [1/4] 检查依赖...
pip show aiofiles >nul 2>&1
if errorlevel 1 (
    echo [警告] aiofiles未安装，正在安装...
    pip install aiofiles
)

echo [2/4] 验证修复...
python test_fixes.py
if errorlevel 1 (
    echo [错误] 验证测试失败，请检查日志
    pause
    exit /b 1
)

echo [3/4] 创建必要目录...
if not exist "..\data\uploads" mkdir "..\data\uploads"

echo [4/4] 启动服务...
echo.
echo ========================================
echo   后端服务运行中...
echo   API文档: http://localhost:8000/docs
echo   健康检查: http://localhost:8000/health
echo ========================================
echo.

python start.py
