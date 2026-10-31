@echo off
setlocal
cd /d "%~dp0"
echo [INFO] Starting False Echo through FEMS.

if exist "%~dp0FEMS.exe" goto use_standalone
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 -c "import sys" >nul 2>nul
  if not errorlevel 1 goto use_py
)
where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] FEMS.exe or Python 3.10+ was not found.
  pause
  exit /b 1
)
goto use_python

:use_standalone
echo [INFO] Using the standalone FEMS application.
"%~dp0FEMS.exe" play %*
goto finish

:use_py
echo [INFO] Using Python 3.
py -3 fems_launcher.py %*
goto finish

:use_python
echo [INFO] Using Python.
python fems_launcher.py %*

:finish
set "FEMS_EXIT=%errorlevel%"
if "%FEMS_EXIT%"=="0" (
  echo [OK] FEMS start command completed.
) else (
  echo [ERROR] FEMS could not start False Echo. Code %FEMS_EXIT%.
  pause
)
exit /b %FEMS_EXIT%
