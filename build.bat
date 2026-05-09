@echo off
pyinstaller --onefile --windowed --name AutoFotoAI --icon NONE main.py
echo.
echo Build fertig. EXE liegt in: dist\AutoFotoAI.exe
pause
