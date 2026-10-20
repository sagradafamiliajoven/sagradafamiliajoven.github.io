@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo  Actualizando el crucigrama con las pistas de herramientas\datos\pistas_propias.xlsx ...
echo.
python herramientas\actualizar_crucigrama.py
if errorlevel 1 goto error
git add herramientas js
git commit -q -m "Crucigrama: pistas propias actualizadas"
git push -q
if errorlevel 1 goto error
echo.
echo  Listo. En uno o dos minutos se ve en la web.
echo.
pause
exit /b

:error
echo.
echo  Hubo un problema: lee el mensaje de arriba y avisale a quien mantiene la web.
echo.
pause
