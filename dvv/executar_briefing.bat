@echo off

cd /d "C:\Users\OMBRO SECRETARIA1\Desktop\AI Build - Teste no VSCode"

"C:\Users\OMBRO SECRETARIA1\Desktop\AI Build - Teste no VSCode\venv\Scripts\python.exe" "dvv\daily_briefing.py" --auto > "dvv\briefing_log.txt" 2>&1

echo Codigo de saida: %ERRORLEVEL% >> "dvv\briefing_log.txt"
