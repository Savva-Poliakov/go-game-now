@echo off
pyinstaller --onefile --noconsole --icon=assets\logo.ico --name GGN --add-data "assets\logo.ico;assets" --add-data "assets\bgm.mp3;assets" src\main.py
if not exist dist\GGN.exe (
    echo Build failed: dist\GGN.exe not found.
    exit /b 1
)
set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %ISCC% (
    set ISCC=ISCC
)
%ISCC% installer\installer.iss
if %errorlevel% neq 0 (
    echo Installer build failed.
    exit /b 1
)
echo Done. Installer is in installer\Output\GGN_Setup.exe
