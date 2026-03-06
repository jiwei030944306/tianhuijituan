@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ========================================
::   智研题库云 - 后端服务启动（带重启机制）
:: ========================================

cd /d %~dp0

:: 配置
set MAX_RESTARTS=5
set RESTART_DELAY=3
set RESTART_COUNT=0

echo ========================================
echo   智研题库云 - 后端服务启动
echo ========================================
echo.
echo   自动重启: 最多 %MAX_RESTARTS% 次
echo   重启延迟: %RESTART_DELAY% 秒
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.11+
    pause
    exit /b 1
)

:: 创建日志目录
if not exist "logs" mkdir "logs"

:: 主循环
:restart_loop

echo ========================================
echo [%date% %time%] 启动后端服务...
echo ========================================

:: 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info

:: 检查退出码
if %errorlevel% equ 0 (
    echo [%date% %time%] 服务正常退出
    goto :end
)

:: 异常退出处理
set /a RESTART_COUNT+=1

echo.
echo ========================================
echo [警告] 服务异常退出，退出码: %errorlevel%
echo 重启次数: %RESTART_COUNT%/%MAX_RESTARTS%
echo ========================================
echo.

:: 记录崩溃日志
echo [%date% %time%] 服务崩溃，退出码: %errorlevel%，重启次数: %RESTART_COUNT% >> logs\crash.log

:: 检查是否超过最大重启次数
if %RESTART_COUNT% geq %MAX_RESTARTS% (
    echo [错误] 超过最大重启次数 (%MAX_RESTARTS%)，停止服务
    echo [%date% %time%] 超过最大重启次数，停止服务 >> logs\crash.log
    goto :end
)

:: 等待后重启
echo %RESTART_DELAY% 秒后自动重启...
timeout /t %RESTART_DELAY% /nobreak >nul
goto :restart_loop

:end
echo.
echo 服务已停止
pause