@echo off
setlocal enabledelayedexpansion

:: === CONFIGURATION ===
set DRIVE_PATH=G:\Shared drives\AFS Drive\AFS Submissions Tool
set GIT_PATH=C:\Users\Matteo\Downloads\AFS Submissions Code
set FINAL_NAME=AFS_Submission_Tool
set RELEASES_FOLDER=%GIT_PATH%\releases
set VERSION_FILE=%GIT_PATH%\info\version.txt

:: === Ensure releases folder exists ===
if not exist "%RELEASES_FOLDER%" (
    mkdir "%RELEASES_FOLDER%"
)

:: === Read and increment patch version ===
set VERSION=0.0.0

if exist "%VERSION_FILE%" (
    set /p VERSION=<"%VERSION_FILE%"
)

echo Current version: %VERSION%

for /f "tokens=1-3 delims=." %%a in ("%VERSION%") do (
    set /a PATCH=%%c + 1
    set MAJOR=%%a
    set MINOR=%%b
)

set VERSION=%MAJOR%.%MINOR%.%PATCH%
echo New patch version: v%VERSION%

:: === Save updated version to version.txt ===
echo %VERSION% > "%VERSION_FILE%"

:: === Build the executable ===
echo Building executable...
pyinstaller --noconfirm AFS-Submissions-Tool.spec

IF %ERRORLEVEL% NEQ 0 (
    echo Build failed.
    pause
    exit /b %ERRORLEVEL%
)

:: === Copy to local releases folder ===
echo Copying to local releases...
copy /y "dist\AFS-Submissions-Tool.exe" "%RELEASES_FOLDER%\%FINAL_NAME%_v%VERSION%.exe"

IF %ERRORLEVEL% NEQ 0 (
    echo Failed to copy to releases folder.
    pause
    exit /b %ERRORLEVEL%
)

:: === Copy to Google Drive (overwrite) ===
echo Copying to Google Drive...
copy /y "dist\AFS-Submissions-Tool.exe" "%DRIVE_PATH%\%FINAL_NAME%.exe"

IF %ERRORLEVEL% NEQ 0 (
    echo Failed to copy to Google Drive.
    pause
    exit /b %ERRORLEVEL%
)

echo Deployment complete!
exit /b 0
