# Solución de Problemas - PyMonitor.NET

## Error: "No se puede cargar el archivo o ensamblado" (0x80131515)

### Síntomas:
```
An unexpected error occurred: No se puede cargar el archivo o ensamblado 'file:///C:\Users\...\LibreHardwareMonitorLib.dll' ni una de sus dependencias. Operación no admitida. (Excepción de HRESULT: 0x80131515)
```

### Causa:
Este error ocurre cuando .NET Framework considera que la aplicación está ejecutándose desde una ubicación "no confiable", típicamente:
- Carpeta de **Descargas**
- Carpetas temporales
- Unidades de red
- Carpetas con nombres que contienen caracteres especiales

### ✅ **Soluciones (en orden de preferencia):**

#### 1. Mover a ubicación confiable (RECOMENDADO)
Mueve toda la carpeta `PyMonitor.NET` a una ubicación confiable:

**Ubicaciones recomendadas:**
```
C:\Program Files\PyMonitor.NET
C:\Users\[TuUsuario]\Documents\PyMonitor.NET
C:\PyMonitor.NET
C:\Tools\PyMonitor.NET
```

**Pasos:**
1. Corta (Ctrl+X) toda la carpeta `PyMonitor.NET-master` o `PyMonitor.NET`
2. Pégala en una de las ubicaciones recomendadas
3. Ejecuta `run.pyw` desde la nueva ubicación

#### 2. Desbloquear archivos DLL
Si no puedes mover la carpeta:

1. Click derecho en `LibreHardwareMonitorLib.dll`
2. Selecciona **Propiedades**
3. En la pestaña **General**, marca **"Desbloquear"** (si aparece)
4. Click **Aceptar**
5. Repite para `HidSharp.dll`

#### 3. Ejecutar como Administrador
Como último recurso:
1. Click derecho en `run.pyw`
2. Selecciona **"Ejecutar como administrador"**

### 🔍 **Prevención:**
- **NO** ejecutes la aplicación directamente desde la carpeta de Descargas
- **NO** uses nombres de carpeta con caracteres especiales
- **SÍ** mueve aplicaciones a ubicaciones permanentes antes de usarlas

---

## Otros Problemas Comunes

### Error: "Could not find LibreHardwareMonitorLib.dll"
**Solución:** Asegúrate de que `LibreHardwareMonitorLib.dll` y `HidSharp.dll` estén en la misma carpeta que `run.pyw`.

### Error: "pythonnet not found" o "PyQt6 not found"
**Solución:** Instala las dependencias:
```bash
pip install -r requirements.txt
```

### La aplicación no aparece en la pantalla
**Solución:** La aplicación se ejecuta en segundo plano. Busca el ícono en la bandeja del sistema (cerca del reloj).

### Error de permisos de administrador
**Solución:** 
1. Algunos sensores de hardware requieren permisos elevados
2. Ejecuta como administrador si es necesario
3. O mueve a una ubicación que no requiera permisos especiales

---

## 📞 Soporte

Si ninguna de estas soluciones funciona:

1. **Verifica la versión de .NET:** El proyecto requiere .NET Framework 4.7.2 o superior
2. **Revisa el antivirus:** Algunos antivirus bloquean archivos DLL
3. **Reporta el problema:** Abre un issue en GitHub con:
   - Tu sistema operativo
   - Ubicación exacta de la carpeta
   - Mensaje de error completo
   - Pasos que ya intentaste

## 🛠️ Información del Sistema
Para reportar problemas, incluye:
- **OS:** Windows 10/11
- **Python:** Versión (ejecuta `python --version`)
- **Ubicación:** Ruta completa donde tienes PyMonitor.NET
- **.NET:** Versión instalada
