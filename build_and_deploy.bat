@echo off
setlocal enabledelayedexpansion

:: === CONFIGURATION ===
set DRIVE_PATH="G:\Shared drives\AFS Drive\AFS Submissions Tool"
set GIT_PATH="C:\Users\Matteo\Downloads\AFS Submissions Code"
set FINAL_NAME=AFS_Submission_Tool
set RELEASES_FOLDER="C:\Users\Matteo\Downloads\AFS Submissions Code\releases"

:: === Ensure releases folder exists ===
if not exist %RELEASES_FOLDER% (
    mkdir %RELEASES_FOLDER%
)

:: === Determine next version ===
echo Checking latest version...

set MAJOR=1
set MINOR=0

set LATEST_MAJOR=0
set LATEST_MINOR=0

for %%f in (%RELEASES_FOLDER%\%FINAL_NAME%_v*.exe) do (
    set "FILENAME=%%~nxf"
    
    echo Processing filename: !FILENAME!
    
    for /f "tokens=4,5 delims=_v." %%a in ('echo !FILENAME!') do (
        echo Extracted Major: %%a  Minor: %%b
        set "CUR_MAJOR=%%a"
        set "CUR_MINOR=%%b"

        rem Compare major
        if !CUR_MAJOR! gtr !LATEST_MAJOR! (
            set /a LATEST_MAJOR=!CUR_MAJOR!
            set /a LATEST_MINOR=!CUR_MINOR!
        ) else if !CUR_MAJOR! == !LATEST_MAJOR! (
            if !CUR_MINOR! gtr !LATEST_MINOR! (
                set /a LATEST_MINOR=!CUR_MINOR!
            )
        )
    )
)

:: If we found any version, increment
if !LATEST_MAJOR! neq 0 (
    set /a LATEST_MINOR+=1
    set MAJOR=!LATEST_MAJOR!
    set MINOR=!LATEST_MINOR!
    echo !MAJOR!.!MINOR!
)

:: Build final version string
set VERSION=%MAJOR%.%MINOR%

echo %VERSION% > version.txt
timeout /t 1 > nul
echo New version: v%VERSION%

:: === Build the executable ===
echo Building executable...
pyinstaller --noconfirm AFS-Submissions-Tool.spec

IF %ERRORLEVEL% NEQ 0 (
    echo Build failed 
    pause
    exit /b %ERRORLEVEL%
)

echo Build successful!

:: === Copy to releases folder ===
echo Copying to local releases...
copy /y "dist\AFS-Submissions-Tool.exe" %RELEASES_FOLDER%\%FINAL_NAME%_v%VERSION%.exe

IF %ERRORLEVEL% NEQ 0 (
    echo Failed to copy to releases folder 
    pause
    exit /b %ERRORLEVEL%
)

:: === Copy to Google Drive (overwrite) ===
echo Copying to Google Drive...
copy /y "dist\AFS-Submissions-Tool.exe" %DRIVE_PATH%\%FINAL_NAME%.exe

IF %ERRORLEVEL% NEQ 0 (
    echo Failed to copy to Google Drive 
    pause
    exit /b %ERRORLEVEL%
)

echo Deployment complete! 
exit
