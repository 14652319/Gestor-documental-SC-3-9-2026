# 🚀 INICIO RÁPIDO - SISTEMAS INDEPENDIENTES

## ✅ SISTEMA LISTO Y FUNCIONAL

Los dos sistemas ahora funcionan **independientemente** en puertos diferentes:

| Sistema              | Puerto | Script de Inicio           |
|---------------------|--------|----------------------------|
| Gestor Documental   | 8099   | `1_iniciar_gestor.bat`    |
| DIAN vs ERP         | 8097   | `2_iniciar_dian.bat`      |

---

## 🎯 INSTRUCCIONES DE USO

### Paso 1: Iniciar Gestor Documental
1. Haz doble clic en: **`1_iniciar_gestor.bat`**
2. Espera a que diga: `Running on http://127.0.0.1:8099`
3. Abre tu navegador: http://localhost:8099

### Paso 2: Iniciar DIAN vs ERP
1. Haz doble clic en: **`2_iniciar_dian.bat`** (en OTRA ventana)
2. Espera a que diga: `Running on http://0.0.0.0:8097`
3. El sistema se abrirá automáticamente o ve a: http://localhost:8097

### Paso 3: Usar Desde el Gestor Documental
1. Inicia sesión en el Gestor Documental
2. En el menú lateral, busca: **⚖️ Validación DIAN vs ERP**
3. Haz clic y se abrirá el sistema en una nueva ventana

---

## 🔗 ACCESO DIRECTO

- **Gestor Documental:** http://localhost:8099
- **DIAN vs ERP:** http://localhost:8097

---

## ⚠️ IMPORTANTE

- **Mantén ambas ventanas CMD abiertas** mientras uses los sistemas
- Para cerrar: presiona `Ctrl+C` en cada ventana CMD o simplemente ciérralas

---

## ✅ CAMBIOS REALIZADOS

1. ✅ Sistemas configurados para trabajar independientemente
2. ✅ Puerto 8099 para Gestor Documental
3. ✅ Puerto 8097 para DIAN vs ERP
4. ✅ Enlace agregado en el menú del dashboard
5. ✅ Scripts de inicio simples creados
6. ✅ Notificación visual al abrir DIAN vs ERP

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### ❌ "Puerto 8099 ya en uso"
```cmd
netstat -ano | findstr :8099
taskkill /PID [numero] /F
```

### ❌ "Puerto 8097 ya en uso"
```cmd
netstat -ano | findstr :8097
taskkill /PID [numero] /F
```

### ❌ "No se puede conectar"
- Verifica que ambos sistemas estén corriendo
- Revisa las ventanas CMD para ver si hay errores
- Asegúrate de que el firewall no bloquee los puertos

---

**Estado:** ✅ FUNCIONAL Y LISTO PARA USAR
**Fecha:** 30 de Noviembre de 2025
