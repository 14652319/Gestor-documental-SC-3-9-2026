# ⚡ GUÍA RÁPIDA DE CONFIGURACIÓN
**Sistema Gestor Documental - Supertiendas Cañaveral**

---

## 🔐 CREDENCIALES DE ACCESO

### Administrador Principal
```
URL: http://127.0.0.1:8099
NIT: 805028041
Usuario: admin
Password: Admin1234$
Rol: admin
```

### Base de Datos PostgreSQL
```
Host: localhost
Puerto: 5432
Base de datos: gestor_documental
Usuario: postgres
Password: G3st0radm$2025.
```

---

## 🚀 INICIAR EL SISTEMA

### 1. Activar entorno virtual e iniciar servidor
```powershell
cd "C:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059"
.\.venv\Scripts\Activate.ps1
python app.py
```

### 2. Acceder al sistema
- **Navegador:** http://127.0.0.1:8099
- **Red local:** http://192.168.11.33:8099

---

## 📧 CONFIGURACIÓN DE CORREO

### ⚠️ IMPORTANTE: Puerto 465 (SSL)
El puerto 587 está **BLOQUEADO** por el firewall. Usar configuración SSL:

```properties
# Archivo: .env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=465
MAIL_USE_TLS=False
MAIL_USE_SSL=True
MAIL_USERNAME=gestordocumentalsc01@gmail.com
MAIL_PASSWORD=urjrkjlogcfdtynq
```

### Probar envío de correo
```powershell
.\.venv\Scripts\python.exe test_smtp_465.py
```

---

## 🗂️ MÓDULO CAUSACIONES

### Carpetas de Red Configuradas

| Sede | Aprobadas | Causadas |
|------|-----------|----------|
| CYS | W:\APROBADAS | W:\CAUSADAS |
| DOM | V:\APROBADAS | V:\CAUSADAS |
| TIC | U:\APROBADAS | U:\CAUSADAS |
| MER | X:\APROBADAS | X:\CAUSADAS |
| MYP | Z:\APROBADAS | Z:\CAUSADAS |
| FIN | T:\APROBADAS | T:\CAUSADAS |

### Acceso al módulo
```
URL: http://127.0.0.1:8099/causaciones/
```

---

## 🔧 SOLUCIÓN DE PROBLEMAS

### Correos no se envían
1. Verificar que el servidor esté usando puerto **465** (no 587)
2. Ejecutar: `python test_smtp_465.py`
3. Revisar logs: `logs/security.log`

### Error de login
- Verificar que el usuario admin esté activo (ID: 23)
- Verificar que el rol sea 'admin' (no 'administrador')

### Carpetas de red no accesibles
- Verificar que las unidades estén mapeadas (W:, V:, U:, X:, Z:, T:)
- Ejecutar: `python test_carpetas_red.py`

### Base de datos no conecta
```powershell
# Verificar que PostgreSQL esté corriendo
Get-Service -Name postgresql*

# Probar conexión
$env:PGPASSWORD="G3st0radm`$2025."
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d gestor_documental -c "SELECT version();"
```

---

## 📋 SCRIPTS DE PRUEBA

| Script | Función |
|--------|---------|
| `test_smtp_465.py` | Probar envío de correo |
| `test_carpetas_red.py` | Verificar acceso a carpetas |
| `ver_config_mail.py` | Ver configuración de correo |
| `verificar_usuario.py` | Verificar datos de usuario |

---

## 🔄 REINICIAR SISTEMA

### 1. Detener servidor
```
Presionar Ctrl+C en la terminal
```

### 2. Reiniciar
```powershell
python app.py
```

### 3. Verificar logs
```
✅ SERVIDOR INICIANDO - Módulos HABILITADOS: Recibir Facturas, Relaciones, Archivo Digital, Causaciones, Monitoreo
```

---

## 📞 INFORMACIÓN DE CONTACTO

**Empresa:** Supertiendas Cañaveral SAS  
**NIT:** 805.028.041-1  
**Sistema:** Gestor Documental v1.0  
**Email:** gestordocumentalsc01@gmail.com

---

**Última actualización:** 14 de Noviembre 2025
