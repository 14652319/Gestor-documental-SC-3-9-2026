# 📍 UBICACIÓN ACTUAL DE TUS ARCHIVOS - FACTURAS DIGITALES

**Fecha:** 8 de diciembre de 2025  
**Problema:** Archivos guardados en ubicación incorrecta

---

## 🔍 DONDE ESTÁN TUS ARCHIVOS AHORA:

### ✅ **UBICACIÓN CORRECTA** - 4 facturas en `D:\facturas_digitales\`:

```
D:\facturas_digitales\
│
├── SC\2025\11. NOVIEMBRE\DOM\
│   └── 805013653-DS-14\           ← ID 2: DS-14 ✅
│       ├── 805013653-DS-14-PRINCIPAL.pdf (59 KB)
│       ├── 805013653-DS-14-ANEXO1.pdf (132 KB)
│       ├── 805013653-DS-14-ANEXO2.pdf (132 KB)
│       ├── 805013653-DS-14-ANEXO3.pdf (87 KB)
│       └── 805013653-DS-14-SEG_SOCIAL.pdf (593 KB)
│
├── SC\2025\12. DICIEMBRE\MER\EST\
│   └── 805013653-FE-12121\        ← ID 3: FE-12121 ✅
│       ├── 805013653-FE-12121-PRINCIPAL.pdf
│       ├── 805013653-FE-12121-ANEXO1.pdf
│       └── 805013653-FE-12121-SEG_SOCIAL.pdf
│
├── SC\2025\12. DICIEMBRE\TIC\EST\
│   └── 14652319-FE-37\            ← ID 4: FE-37 ✅
│       ├── 14652319-FE-37-PRINCIPAL.pdf
│       ├── 14652319-FE-37-ANEXO1.pdf
│       └── 14652319-FE-37-SEG_SOCIAL.pdf
│
└── LG\2025\12. DICIEMBRE\CYS\EST\
    └── 14652319-FE-36\            ← ID 5: FE-36 ✅
        ├── 14652319-FE-36-PRINCIPAL.pdf
        ├── 14652319-FE-36-ANEXO1.pdf
        └── 14652319-FE-36-SEG_SOCIAL.pdf
```

---

### ❌ **UBICACIÓN INCORRECTA** - 3 facturas en `D:\2025\` (falta /facturas_digitales/):

```
D:\2025\
└── 12. DICIEMBRE\
    │
    ├── 14652319-FE-13\            ← ID 6: FE-13 ❌
    │   ├── 14652319-FE-13-PRINCIPAL.pdf (825 KB)
    │   ├── 14652319-FE-13-ANEXO1.pdf
    │   └── 14652319-FE-13-SEG_SOCIAL.pdf
    │
    ├── 14652319-FE-44\            ← ID 7: FE-44 ❌
    │   ├── 14652319-FE-44-PRINCIPAL.pdf (622 KB)
    │   ├── 14652319-FE-44-ANEXO1.pdf
    │   └── 14652319-FE-44-SEG_SOCIAL.pdf
    │
    └── 14652319-XE-25\            ← ID 8: XE-25 ❌ (recién cargado)
        ├── 14652319-XE-25-PRINCIPAL.pdf (622 KB)
        ├── 14652319-XE-25-ANEXO1.pdf
        └── 14652319-XE-25-SEG_SOCIAL.pdf
```

---

## ⚠️ ¿POR QUÉ PASÓ ESTO?

Las facturas **FE-13, FE-44 y XE-25** se guardaron en `D:\2025\` porque:

1. **NO se especificó EMPRESA** al cargar la factura
2. **NO se especificó DEPARTAMENTO** al cargar la factura
3. El código anterior tenía un bug: cuando faltaban estos campos, construía rutas como:
   ```python
   D:/ + "" + 2025 + 12 + "" + "" + NIT-PREFIJO-FOLIO
   = D:/2025/12///14652319-FE-44/
   ```

---

## ✅ LO QUE YA CORREGÍ:

### 1. **Código corregido en `routes.py`:**
   - ✅ Ahora usa valores por defecto: `SIN_EMPRESA`, `SIN_DEPARTAMENTO`, `SIN_FORMA_PAGO`
   - ✅ Estructura correcta: `D:/facturas_digitales/EMPRESA/AÑO/MES/DEPARTAMENTO/FORMA_PAGO/`
   - ✅ Función `crear_estructura_carpetas()` actualizada con la lógica correcta

### 2. **Carpeta TEMPORALES creada:**
   - ✅ `D:\facturas_digitales\TEMPORALES\` existe y lista para usuarios externos

---

## 🛠️ LO QUE DEBES HACER AHORA:

### **OPCIÓN 1: Mover manualmente los archivos (RECOMENDADO)**

Abre PowerShell y ejecuta:

```powershell
# Mover FE-13
Move-Item "D:\2025\12. DICIEMBRE\14652319-FE-13" `
          "D:\facturas_digitales\SIN_EMPRESA\2025\12\SIN_DEPARTAMENTO\SIN_FORMA_PAGO\" -Force

# Mover FE-44
Move-Item "D:\2025\12. DICIEMBRE\14652319-FE-44" `
          "D:\facturas_digitales\SIN_EMPRESA\2025\12\SIN_DEPARTAMENTO\SIN_FORMA_PAGO\" -Force

# Mover XE-25
Move-Item "D:\2025\12. DICIEMBRE\14652319-XE-25" `
          "D:\facturas_digitales\SIN_EMPRESA\2025\12\SIN_DEPARTAMENTO\SIN_FORMA_PAGO\" -Force
```

Luego actualiza la base de datos:
```powershell
python actualizar_rutas_facturas.py
```

---

### **OPCIÓN 2: Completar los campos de estas facturas en el sistema**

1. Abre el módulo **Facturas Digitales**
2. Busca las facturas **FE-13, FE-44, XE-25**
3. Click en **"Completar Campos"**
4. Llena:
   - Empresa: SC, LG, etc.
   - Departamento: TIC, DOM, etc.
   - Forma Pago: CREDITO, CONTADO, etc.
5. Click en **"Guardar"**
6. El sistema automáticamente:
   - Moverá los archivos de `D:\2025\` a la ubicación correcta
   - Actualizará la base de datos

---

### **OPCIÓN 3: Usar el script automático** (si funciona)

```powershell
python mover_archivos_mal_ubicados.py
```

Este script:
- ✅ Busca facturas en ubicación incorrecta
- ✅ Las mueve a `D:\facturas_digitales\SIN_EMPRESA\2025\12\SIN_DEPARTAMENTO\SIN_FORMA_PAGO\`
- ✅ Actualiza la base de datos automáticamente

---

## 📋 RESUMEN:

| Factura | Ubicación Actual | Ubicación Correcta | Estado |
|---------|------------------|-------------------|--------|
| ID 2: DS-14 | `D:\facturas_digitales\SC\...` | ✅ Correcta | OK |
| ID 3: FE-12121 | `D:\facturas_digitales\SC\...` | ✅ Correcta | OK |
| ID 4: FE-37 | `D:\facturas_digitales\SC\...` | ✅ Correcta | OK |
| ID 5: FE-36 | `D:\facturas_digitales\LG\...` | ✅ Correcta | OK |
| ID 6: FE-13 | `D:\2025\12. DICIEMBRE\...` | ❌ Incorrecta | **MOVER** |
| ID 7: FE-44 | `D:\2025\12. DICIEMBRE\...` | ❌ Incorrecta | **MOVER** |
| ID 8: XE-25 | `D:\2025\12. DICIEMBRE\...` | ❌ Incorrecta | **MOVER** |

---

## 🚀 PARA EL FUTURO:

A partir de ahora, **TODAS las facturas nuevas** se guardarán correctamente en:

```
D:/facturas_digitales/
├── TEMPORALES/                    ← Usuarios EXTERNOS
│   └── {NIT}/
│       └── {NIT-PREFIJO-FOLIO}/
│
├── {EMPRESA}/                     ← Usuarios INTERNOS
│   └── {AÑO}/
│       └── {MES}/
│           └── {DEPARTAMENTO}/
│               └── {FORMA_PAGO}/
│                   └── {NIT-PREFIJO-FOLIO}/
│
└── SIN_EMPRESA/                   ← Si falta empresa
    └── 2025/
        └── 12/
            └── SIN_DEPARTAMENTO/
                └── SIN_FORMA_PAGO/
```

---

**Última actualización:** 8 de diciembre de 2025 - 22:10
