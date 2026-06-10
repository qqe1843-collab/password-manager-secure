#!/bin/bash
# Script для сборки Password Manager Secure в EXE файл (Linux/Mac)
# Убедитесь, что у вас установлены все зависимости:
# pip install -r requirements-build.txt

echo "========================================"
echo "Password Manager Secure - Builder"
echo "========================================"
echo ""

# Очищаем старые сборки
echo "Удаляю старые сборки..."
rm -rf build dist *.spec

echo ""
echo "Запускаю PyInstaller..."
pyinstaller --onefile \
    --windowed \
    --name="Password Manager Secure" \
    --distpath "./dist" \
    --buildpath "./build" \
    main.py

echo ""
if [ -f "dist/Password Manager Secure" ]; then
    echo "✓ Приложение успешно создано!"
    echo "Путь: dist/Password Manager Secure"
    echo ""
    echo "Вы можете распространять этот файл!"
else
    echo "✗ Ошибка при создании приложения"
fi
