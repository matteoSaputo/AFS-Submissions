@echo off
setlocal enabledelayedexpansion

REM ===============================
REM functions at the bottom; jump to main
REM ===============================
goto :main

:copy_dir
REM %1 = source dir, %2 = dest dir
if "%~1"=="" ( echo [copy_dir] Missing source & exit /b 9001 )
if "%~2"=="" ( echo [copy_dir] Missing destination & exit /b 9002 )
set "SRC=%~1"
set "DST=%~2"

if not exist "%SRC%" (
  echo [copy_dir] Source not found: "%SRC%"
  exit /b 9003
)

echo [copy_dir] %SRC%  -->  %DST%
robocopy "%SRC%" "%DST%" /E /NFL /NDL /NJH /NJS /NP
set "RC=%ERRORLEVEL%"
REM Robocopy: 0–7 success, >=8 failure
if %RC% GEQ 8 (
  echo [copy_dir] FAILED (robocopy code %RC%)
  exit /b %RC%
)
echo [copy_dir] OK (robocopy code %RC%)
exit /b 0

:main

:: === CONFIGURATION ===
set "DRIVE_PATH=G:\Shared drives\AFS Drive\AFS Submissions Tool"
set "GIT_PATH=C:\Users\Matteo\Downloads\AFS Submissions Code"
set "FINAL_NAME=AFS_Submission_Tool"
set "RELEASES_FOLDER=%GIT_PATH%\releases"
set "INTEGRATIONS_FOLDER=%GIT_PATH%\integrations"
set "VERSION_FILE=%GIT_PATH%\info\version.txt"

:: === Ensure releases folder exists ===
if not exist "%RELEASES_FOLDER%" mkdir "%RELEASES_FOLDER%"

:: === Read and increment minor version ===
set "VERSION=0.0.0"
if exist "%VERSION_FILE%" set /p VERSION=<"%VERSION_FILE%"
echo Current version: %VERSION%

for /f "tokens=1-3 delims=." %%a in ("%VERSION%") do (
    set /a MINOR=%%b + 1
    set "MAJOR=%%a"
)
set "PATCH=0"
set "VERSION=%MAJOR%.%MINOR%.%PATCH%"
echo New minor version: v%VERSION%

:: === Save updated version to version.txt ===
> "%VERSION_FILE%" echo %VERSION%

:: === Build the executable ===
echo Building executable...
pyinstaller --noconfirm AFS-Submissions-Tool.spec
IF %ERRORLEVEL% NEQ 0 ( echo Build failed. & pause & exit /b %ERRORLEVEL% )

:: === Copy EXE to local releases ===
echo Copying to local releases...
copy /y "dist\AFS-Submissions-Tool.exe" "%RELEASES_FOLDER%\%FINAL_NAME%_v%VERSION%.exe" >nul
IF %ERRORLEVEL% NEQ 0 ( echo Failed to copy to releases folder. & pause & exit /b %ERRORLEVEL% )

:: === Copy integrations -> releases\integrations  (with logging) ===
echo Copying integrations to releases...
call :copy_dir "%INTEGRATIONS_FOLDER%" "%RELEASES_FOLDER%\integrations" "%RELEASES_FOLDER%\robocopy_integrations_to_releases.log"
IF %ERRORLEVEL% GEQ 8 ( echo Failed to copy integrations to releases. See log. & pause & exit /b %ERRORLEVEL% )

:: === Copy EXE to Google Drive (overwrite) ===
echo Copying to Google Drive...
copy /y "dist\AFS-Submissions-Tool.exe" "%DRIVE_PATH%\%FINAL_NAME%.exe" >nul
IF %ERRORLEVEL% NEQ 0 ( echo Failed to copy to Google Drive. & pause & exit /b %ERRORLEVEL% )

:: === Copy integrations -> Drive\integrations ===
echo Copying integrations to Google Drive...
call :copy_dir "%INTEGRATIONS_FOLDER%" "%DRIVE_PATH%\integrations" "%DRIVE_PATH%\robocopy_integrations_to_drive.log"
IF %ERRORLEVEL% GEQ 8 ( echo Failed to copy integrations to Drive. See log. & pause & exit /b %ERRORLEVEL% )

echo Deployment complete!
exit /b 0
