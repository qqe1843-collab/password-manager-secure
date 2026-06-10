@echo off
REM Script для сборки Password Manager Secure в EXE файл
REM Убедитесь, что у вас установлены все зависимости:
REM pip install -r requirements-build.txt

echo ========================================
echo Password Manager Secure - Builder
echo ========================================
echo.

REM Очищаем старые сборки
echo Удаляю старые сборки...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q *.spec 2>nul

echo.
echo Запускаю PyInstaller...
pyinstaller --onefile ^
    --windowed ^
    --icon=icon.ico ^
    --name="Password Manager Secure" ^
    --add-data "password_manager:password_manager" ^
    --distpath "./dist" ^
    --buildpath "./build" ^
    main.py

echo.
if exist "dist\Password Manager Secure.exe" (
    echo ✓ EXE файл успешно создан!
    echo Путь: dist\Password Manager Secure.exe
    echo.
    echo Вы можете скачать и распространять этот файл!
) else (
    echo ✗ Ошибка при создании EXE файла
    pause
)

pause
