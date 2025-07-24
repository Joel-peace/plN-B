@echo off
echo ================================
echo  FARMART BACKEND - GITHUB UPLOAD
echo ================================

echo.
echo 1. Checking if Git is available...
git --version
if %errorlevel% neq 0 (
    echo ERROR: Git is not available. Please restart your terminal or computer.
    pause
    exit /b 1
)

echo.
echo 2. Cloning your repository...
cd ..
git clone git@github.com:Joel-peace/plN-B.git
if %errorlevel% neq 0 (
    echo ERROR: Failed to clone repository. Check your SSH keys.
    pause
    exit /b 1
)

echo.
echo 3. Creating farmart-backend directory...
cd plN-B
mkdir farmart-backend 2>nul

echo.
echo 4. Copying files...
xcopy /E /I /Y ..\farmart-backend\*.py farmart-backend\
xcopy /E /I /Y ..\farmart-backend\routes farmart-backend\routes\
copy ..\farmart-backend\README.md farmart-backend\
copy ..\farmart-backend\requirements*.txt farmart-backend\
copy ..\farmart-backend\.env.example farmart-backend\ 2>nul
copy ..\farmart-backend\.gitignore farmart-backend\ 2>nul

echo.
echo 5. Adding files to Git...
git add .

echo.
echo 6. Committing changes...
git commit -m "Add Farmart Backend API (Part 2) - Complete Flask backend with authentication, animal management, cart, and orders"

echo.
echo 7. Pushing to GitHub...
git push origin main

echo.
echo ================================
echo  UPLOAD COMPLETED SUCCESSFULLY!
echo ================================
pause
