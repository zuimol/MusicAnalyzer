@echo off
chcp 65001 >nul
echo.
echo 🎵 音乐升级下载工具 - 快速启动
echo ================================================
echo.
echo 选择要运行的工具：
echo.
echo 1. 启动 Streamlit Web 应用 (app.py)
echo 2. 生成下载清单 (export_download_list.py)
echo 3. 打开导出文件夹
echo 4. 查看下载指南
echo 5. 退出
echo.
set /p choice="请输入选择 (1-5): "

if "%choice%"=="1" (
    echo.
    echo ▶️  启动 Streamlit 应用...
    echo 📂 打开浏览器访问: http://localhost:8501
    echo.
    D:/WorkDepend/miniconda/python.exe -m streamlit run app.py
    exit /b
)

if "%choice%"=="2" (
    echo.
    echo ▶️  生成下载清单...
    echo.
    D:/WorkDepend/miniconda/python.exe export_download_list.py
    echo.
    pause
    exit /b
)

if "%choice%"=="3" (
    echo.
    echo 📂 打开导出文件夹...
    start explorer exports
    exit /b
)

if "%choice%"=="4" (
    echo.
    echo 📖 打开下载指南...
    start DOWNLOAD_GUIDE.md
    exit /b
)

if "%choice%"=="5" (
    exit /b
)

echo 无效选择，请重新运行。
pause
