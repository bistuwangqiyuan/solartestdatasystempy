@echo off
echo ============================================
echo 启动光伏关断器检测数据管理系统
echo ============================================
echo.

REM 设置环境变量
set SUPABASE_URL=https://zzyueuweeoakopuuwfau.supabase.co
set SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6eXVldXdlZW9ha29wdXV3ZmF1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQzODEzMDEsImV4cCI6MjA1OTk1NzMwMX0.y8V3EXK9QVd3txSWdE3gZrSs96Ao0nvpnd0ntZw_dQ4
set SUPABASE_SERVICE_KEY=%SUPABASE_ANON_KEY%
set SECRET_KEY=solar-test-data-system-secret-key-2025

echo [1/2] 启动后端服务...
start "Backend Server" cmd /k "cd backend && echo 启动FastAPI... && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo 等待后端启动...
timeout /t 5 /nobreak > nul

echo.
echo [2/2] 启动前端服务...
start "Frontend Server" cmd /k "cd frontend && echo 启动React开发服务器... && npm run dev"

echo.
echo ============================================
echo 服务启动完成！
echo.
echo 后端地址: http://localhost:8000
echo API文档: http://localhost:8000/api/v1/docs
echo 前端地址: http://localhost:3000
echo ============================================
echo.
pause
