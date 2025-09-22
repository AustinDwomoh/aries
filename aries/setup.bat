@echo off
echo 🚀 Setting up Aries Gaming Platform - Modern TypeScript Edition
echo ================================================================

REM Check if we're in the right directory
if not exist "manage.py" (
    echo ❌ Error: Please run this script from the Django project root directory
    pause
    exit /b 1
)

echo 📦 Installing Python dependencies...
pip install -r requirements.txt

echo 🗄️ Running Django migrations...
python manage.py makemigrations
python manage.py migrate

echo 👤 Creating superuser (optional)...
echo You can skip this step by pressing Ctrl+C
python manage.py createsuperuser

echo 📁 Setting up frontend dependencies...
cd ..
npm install

echo 🎉 Setup complete!
echo.
echo To start the development servers:
echo 1. Backend: python manage.py runserver
echo 2. Frontend: npm run dev
echo.
echo Access the application at: http://localhost:3000
echo Django admin at: http://localhost:8000/admin
echo.
echo Happy coding! 🎮
pause
