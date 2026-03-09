@echo off
echo ================================================
echo CONFIGURANDO FIREWALL PARA PERMITIR SMTP/Gmail
echo ================================================
echo.
echo Este script creara una regla en el Firewall de Windows
echo para permitir conexiones salientes al puerto 587 (SMTP).
echo.
pause

echo.
echo Creando regla de salida para puerto 587...
netsh advfirewall firewall add rule name="Gmail SMTP Outbound" dir=out action=allow protocol=TCP remoteport=587

echo.
echo Verificando la regla...
netsh advfirewall firewall show rule name="Gmail SMTP Outbound"

echo.
echo ================================================
echo REGLA CREADA EXITOSAMENTE
echo ================================================
echo.
echo Ahora intenta nuevamente el envio de correos.
echo.
pause
