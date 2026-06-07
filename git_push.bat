@echo off
echo ==========================================
echo  AutoEngage - Git Push (Upload Code)
echo ==========================================
echo.
echo Current git status:
git status -s
echo.
set /p commit_msg="Enter commit message (or press Enter for 'Auto-commit'): "
if "%commit_msg%"=="" set commit_msg=Auto-commit

echo.
echo Staging all changes...
git add .

echo.
echo Committing changes...
git commit -m "%commit_msg%"

echo.
echo Pushing changes to GitHub...
git push origin main

echo.
echo ==========================================
echo  Operation finished.
echo ==========================================
pause
