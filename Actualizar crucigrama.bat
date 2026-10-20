@echo off
rem Sin "chcp 65001": con ese modo la consola se cierra sola cuando Python escribe tildes.
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
echo.
echo  Actualizando el crucigrama con las pistas de herramientas\datos\pistas_propias.xlsx ...
echo  (tarda uno o dos minutos)
echo.
python herramientas\actualizar_crucigrama.py
if errorlevel 1 goto error
echo.
echo  Subiendo a la web...
git add herramientas js
git commit -q -m "Crucigrama: pistas propias actualizadas"
git push -q
if errorlevel 1 goto error
echo.
echo  LISTO. En uno o dos minutos se ve en la web.
echo.
pause
exit /b

:error
echo.
echo  Hubo un problema: lee el mensaje de arriba (o sacale una foto) y avisale a quien mantiene la web.
echo.
pause
