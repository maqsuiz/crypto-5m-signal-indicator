@echo off
chcp 65001 >nul
echo ════════════════════════════════════════════════════════
echo     AGS PRO Discord Bot Başlatılıyor...
echo ════════════════════════════════════════════════════════
echo.
cd /d "%~dp0"
"C:\Users\FSOS\AppData\Local\Programs\Python\Python314\python.exe" -u ags_discord_bot.py
pause
