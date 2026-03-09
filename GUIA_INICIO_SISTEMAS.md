# 🚀 GUÍA DE INICIO - SISTEMAS INDEPENDIENTES

## 📋 Descripción

Este paquete contiene **DOS sistemas Flask independientes**:

1. **Gestor Documental** (Puerto 8099) - Sistema principal
2. **DIAN vs ERP** (Puerto 8097) - Sistema de validación de facturas

---

## ⚡ INICIO RÁPIDO (RECOMENDADO)

### Opción 1: Script Automático

**Haz doble clic en:** `iniciar_ambos_sistemas.bat`

Este script:
- ✅ Inicia automáticamente ambos sistemas
- ✅ Abre los navegadores en los puertos correctos
- ✅ Mantiene ambos sistemas funcionando

---

## 🔧 INICIO MANUAL

### 1. Iniciar Gestor Documental (Puerto 8099)

```cmd
cd "C:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059"
.venv\Scripts\activate
python app.py
```

**Acceso:** http://localhost:8099

### 2. Iniciar DIAN vs ERP (Puerto 8097)

**En OTRA terminal CMD:**

```cmd
cd "C:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059\Proyecto Dian Vs ERP v5.20251130"
python app.py
```

**Acceso:** http://localhost:8097

---

## 🔗 INTEGRACIÓN

### Desde el Gestor Documental:

1. Inicia sesión en: http://localhost:8099
2. En el menú lateral, busca: **⚖️ Validación DIAN vs ERP**
3. Haz clic para abrir el sistema en una nueva ventana

**Nota:** Asegúrate de que AMBOS sistemas estén corriendo.

---

## 📊 PUERTOS UTILIZADOS

| Sistema              | Puerto | URL                      |
|---------------------|--------|--------------------------|
| Gestor Documental   | 8099   | http://localhost:8099   |
| DIAN vs ERP         | 8097   | http://localhost:8097   |

---

## 🛑 DETENER LOS SISTEMAS

### Si usaste el script automático:
- Cierra las ventanas CMD que se abrieron

### Si iniciaste manualmente:
- Presiona `Ctrl+C` en cada terminal CMD

---

## ⚠️ SOLUCIÓN DE PROBLEMAS

### Error: "Puerto 8099 ya en uso"
```cmd
netstat -ano | findstr :8099
taskkill /PID [numero_de_proceso] /F
```

### Error: "Puerto 8097 ya en uso"
```cmd
netstat -ano | findstr :8097
taskkill /PID [numero_de_proceso] /F
```

### El sistema DIAN vs ERP no abre desde el Gestor
1. Verifica que DIAN vs ERP esté corriendo en puerto 8097
2. Abre manualmente: http://localhost:8097
3. Revisa la consola del navegador (F12) para errores

---

## 📁 ESTRUCTURA DE ARCHIVOS

```
GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059/
├── app.py                           # ⭐ Gestor Documental (Puerto 8099)
├── .venv/                           # Entorno virtual
├── templates/
│   └── dashboard.html               # ✅ Incluye enlace a DIAN vs ERP
├── Proyecto Dian Vs ERP v5.20251130/
│   ├── app.py                       # ⭐ DIAN vs ERP (Puerto 8097)
│   ├── maestro/                     # Base de datos SQLite
│   └── uploads/                     # Archivos cargados
└── iniciar_ambos_sistemas.bat      # ⚡ Script de inicio automático
```

---

## 💡 NOTAS IMPORTANTES

1. **Virtualenv:** Solo el Gestor Documental usa virtualenv (`.venv`)
2. **Bases de datos:**
   - Gestor Documental: PostgreSQL
   - DIAN vs ERP: SQLite (en `maestro/`)
3. **Configuración:**
   - Gestor Documental: `.env` (configuración global)
   - DIAN vs ERP: `config_smtp.json` (configuración local)

---

## ✅ CHECKLIST DE VERIFICACIÓN

- [ ] Ambos sistemas inician sin errores
- [ ] Gestor Documental accesible en http://localhost:8099
- [ ] DIAN vs ERP accesible en http://localhost:8097
- [ ] El enlace en el menú lateral abre DIAN vs ERP
- [ ] Las bases de datos se conectan correctamente

---

## 📞 SOPORTE

Si tienes problemas:

1. Revisa los logs en las terminales CMD
2. Verifica que los puertos estén libres
3. Asegúrate de tener Python instalado
4. Verifica las dependencias: `pip install -r requirements.txt`

---

**Última actualización:** 30 de Noviembre de 2025
**Versión:** 1.0 - Sistemas Independientes Funcionales
