@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo   Iniciando Video 4K Resizer & Reverse
echo ==========================================

:: Verificar si el servidor ya esta corriendo (opcional, pero ayuda)
:: start /b python app.py > nul 2>&1

echo Lanzando servidor Backend...
start "Video 4K Resizer Server" python app.py

echo Esperando a que el servidor este listo...
timeout /t 5 /nobreak > nul

echo Abriendo aplicacion en el navegador...
start http://127.0.0.1:5000

echo.
echo [INFO] La aplicacion esta activa. 
echo [INFO] No cierres la ventana negra que se abrio (el servidor).
echo [INFO] Puedes minimizar esta ventana.
echo.
pause
