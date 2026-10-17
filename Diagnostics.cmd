@echo off
if not exist "%~dp0service\.venv\Scripts\python.exe" (
  echo Celious environment missing. Use Install.cmd or the documented Python setup command.
  exit /b 1
)
"%~dp0service\.venv\Scripts\python.exe" -B "%~dp0service\diagnostics.py" %*
exit /b %errorlevel%
