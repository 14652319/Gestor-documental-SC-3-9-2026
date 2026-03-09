# 🚀 GUÍA RÁPIDA: INICIAR AMBOS SISTEMAS

## ✅ MÉTODO SIMPLE Y EFECTIVO

### Paso 1: Abrir PowerShell
- Presiona `Windows + X`
- Selecciona "Windows PowerShell" o "Terminal"

### Paso 2: Iniciar Gestor Documental (Puerto 8099)
```powershell
cd 'c:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059'
.\.venv\Scripts\activate
python app.py
```

**📌 IMPORTANTE:** No cierres esta ventana, déjala abierta.

###Paso 3: Abrir SEGUNDA terminal PowerShell
- Presiona de nuevo `Windows + X`
- Selecciona "Windows PowerShell" o "Terminal" otra vez

### Paso 4: Iniciar DIAN vs ERP (Puerto 8097)
```powershell
cd 'c:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059\Proyecto Dian Vs ERP v5.20251130'
python app.py
```

**📌 IMPORTANTE:** No cierres esta ventana tampoco.

### Paso 5: Verificar que ambos estén activos
Abre una tercera terminal y ejecuta:
```powershell
netstat -ano | Select-String ":8099"
netstat -ano | Select-String ":8097"
```

Deberías ver:
```
TCP    0.0.0.0:8099    0.0.0.0:0    LISTENING    XXXXX
TCP    0.0.0.0:8097    0.0.0.0:0    LISTENING    YYYYY
```

### Paso 6: Abrir en navegador
```
http://localhost:8099
```

---

## 🎯 MÉTODO ALTERNATIVO: Archivos .bat

### Opción 1: Doble click en cada archivo
1. Doble click en `1_iniciar_gestor.bat`
2. Esperar 5 segundos
3. Doble click en `2_iniciar_dian.bat`
4. Esperar 5 segundos
5. Abrir navegador en http://localhost:8099

### Opción 2: Usar el iniciador automático
1. Doble click en `iniciar_ambos_sistemas.bat`
2. Esperar 10 segundos
3. Se abrirán 2 ventanas CMD
4. El navegador se abrirá automáticamente

**⚠️ NOTA:** El .bat puede fallar si Python no está en el PATH del sistema.

---

## 🔧 SOLUCIÓN DE PROBLEMAS

### Problema: "Puerto 8099 ya está en uso"
**Solución:**
```powershell
Get-Process python* | Stop-Process -Force
```
Esperar 3 segundos y volver a intentar.

### Problema: "No se reconoce como comando"
**Causa:** Python no está en el PATH
**Solución:**
1. Abrir ventana donde funciona Python
2. Ejecutar: `(Get-Command python).Path`
3. Agregar esa ruta al PATH del sistema

### Problema: Puerto 8097 no levanta
**Causa más común:** La carpeta "Proyecto Dian Vs ERP v5.20251130" no existe o tiene otro nombre

**Verificar:**
```powershell
cd 'c:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059'
dir | Select-String "Proyecto"
```

---

## 📊 VERIFICACIÓN RÁPIDA

### Ver si los servidores están corriendo:
```powershell
Write-Host "`nPuerto 8099 (Gestor):" -ForegroundColor Yellow
if (netstat -ano | Select-String ":8099" | Select-String "LISTENING") {
    Write-Host "✅ ACTIVO" -ForegroundColor Green
} else {
    Write-Host "❌ INACTIVO" -ForegroundColor Red
}

Write-Host "`nPuerto 8097 (DIAN):" -ForegroundColor Yellow
if (netstat -ano | Select-String ":8097" | Select-String "LISTENING") {
    Write-Host "✅ ACTIVO" -ForegroundColor Green
} else {
    Write-Host "❌ INACTIVO" -ForegroundColor Red
}
```

---

## 💡 TIPS

1. **Dos terminales separadas:** Es más confiable que un .bat que intenta abrir ambos
2. **Dejar abiertas:** NO cierres las ventanas de terminal mientras uses los sistemas
3. **Orden:** Inicia primero el Gestor (8099) y luego el DIAN (8097)
4. **Esperar:** Dale 5-10 segundos a cada servidor para que inicie completamente
5. **Verificar:** Usa `netstat` para confirmar que ambos puertos estén en LISTENING

---

## 🎯 RESUMEN EJECUTIVO

**Si tienes prisa:**
1. Abre 2 terminales PowerShell
2. En la primera: Ir a raíz → activar .venv → python app.py
3. En la segunda: Ir a carpeta "Proyecto Dian Vs ERP v5.20251130" → python app.py
4. Abrir http://localhost:8099
5. ¡Listo!

**Duración total:** 30 segundos

---

**Fecha:** 30 de Noviembre 2025
