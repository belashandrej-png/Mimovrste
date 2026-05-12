@echo off
chcp 65001 >nul
color 0A
title Mimovrste Analytics - Auto Installer

cls
echo.
echo ================================================
echo    Mimovrste Analytics Platform
echo    Автоматическая установка и запуск
echo ================================================
echo.

REM Шаг 1: Проверка Python
echo [1/5] Проверка Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ОШИБКА: Python не найден!
    echo.
    echo 1. Откройте браузер
    echo 2. Перейдите: https://python.org/downloads/
    echo 3. Скачайте и установите Python
    echo 4. ВАЖНО: Поставьте галочку "Add Python to PATH"
    echo 5. Перезапустите этот файл
    echo.
    pause
    exit /b 1
)
echo ✓ Python найден
echo.

REM Шаг 2: Установка зависимостей
echo [2/5] Установка библиотек...
echo    (Пожалуйста, подождите 3-5 минут...)
echo.
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo.
    echo ОШИБКА при установке библиотек!
    echo Попробуйте запустить от имени администратора
    pause
    exit /b 1
)
echo ✓ Все библиотеки установлены
echo.

REM Шаг 3: Скачивание данных из облака
echo [3/5] Скачивание данных из облака...
echo    (Это может занять 5-15 минут в зависимости от интернета...)
echo.
python download_data.py
if %errorlevel% neq 0 (
    echo.
    echo ОШИБКА при скачивании данных!
    echo Проверьте подключение к интернету
    pause
    exit /b 1
)
echo ✓ Данные загружены
echo.

REM Шаг 4: Проверка файла
echo [4/5] Проверка файла данных...
if not exist "data\mimodump-dataset.csv" (
    echo.
    echo ОШИБКА: Файл данных не найден!
    pause
    exit /b 1
)
echo ✓ Файл найден
echo.

REM Шаг 5: Запуск дашборда
echo [5/5] Запуск дашборда...
echo.
echo ================================================
echo    Открывается браузер с аналитикой...
echo    URL: http://localhost:8501
echo ================================================
echo.
echo Не закрывайте это окно во время работы!
echo Для остановки нажмите Ctrl+C
echo.

streamlit run dashboard.py --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false

pause
