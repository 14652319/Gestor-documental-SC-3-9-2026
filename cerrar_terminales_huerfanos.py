"""
Script para cerrar terminales PowerShell y Python huerfanos en VS Code

Fecha: 26 de Febrero 2026
Autor: Ricardo Riascos
Proposito: Limpiar terminales idle que consumen memoria innecesariamente
"""

import subprocess
import sys

def cerrar_terminales_huerfanos():
    """Cierra procesos PowerShell y Python con 0% CPU (idle)"""
    
    print("=" * 70)
    print("LIMPIEZA DE TERMINALES HUERFANOS")
    print("=" * 70)
    print()
    
    # Obtener procesos PowerShell con 0% CPU
    comando_ps = """
    Get-Process -Name powershell -ErrorAction SilentlyContinue |
    Where-Object { $_.CPU -eq 0 -and $_.WorkingSet -lt 2MB } |
    Select-Object Id, ProcessName, @{Name='Memory(MB)';Expression={[math]::Round($_.WorkingSet/1MB,2)}}, CPU
    """
    
    print("[1/3] Buscando procesos PowerShell idle...")
    try:
        resultado = subprocess.run(
            ['powershell', '-Command', comando_ps],
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8',
            errors='replace'
        )
        
        lineas = resultado.stdout.strip().split('\n')
        procesos_ps = []
        
        # Parsear salida (saltar headers)
        for linea in lineas[3:]:  # Saltar headers
            if linea.strip():
                partes = linea.split()
                if len(partes) >= 2 and partes[0].isdigit():
                    procesos_ps.append(int(partes[0]))
        
        print(f"   Encontrados: {len(procesos_ps)} procesos PowerShell idle")
        
    except Exception as e:
        print(f"   [ERROR] No se pudo listar procesos PowerShell: {e}")
        procesos_ps = []
    
    # Obtener procesos Python con 0% CPU (excluyendo este script)
    comando_py = """
    Get-Process -Name python -ErrorAction SilentlyContinue |
    Where-Object { $_.CPU -eq 0 -and $_.WorkingSet -lt 50MB } |
    Select-Object Id, ProcessName, @{Name='Memory(MB)';Expression={[math]::Round($_.WorkingSet/1MB,2)}}, CPU
    """
    
    print("[2/3] Buscando procesos Python idle...")
    try:
        resultado = subprocess.run(
            ['powershell', '-Command', comando_py],
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8',
            errors='replace'
        )
        
        lineas = resultado.stdout.strip().split('\n')
        procesos_py = []
        pid_actual = subprocess.os.getpid()
        
        # Parsear salida
        for linea in lineas[3:]:
            if linea.strip():
                partes = linea.split()
                if len(partes) >= 2 and partes[0].isdigit():
                    pid = int(partes[0])
                    if pid != pid_actual:  # NO matar este script
                        procesos_py.append(pid)
        
        print(f"   Encontrados: {len(procesos_py)} procesos Python idle")
        
    except Exception as e:
        print(f"   [ERROR] No se pudo listar procesos Python: {e}")
        procesos_py = []
    
    # Cerrar procesos
    print()
    print("[3/3] Cerrando procesos idle...")
    print()
    
    total_cerrados = 0
    memoria_liberada = 0.0
    
    # Cerrar PowerShell
    for pid in procesos_ps:
        try:
            subprocess.run(
                ['powershell', '-Command', f'Stop-Process -Id {pid} -Force -ErrorAction SilentlyContinue'],
                capture_output=True,
                timeout=5
            )
            total_cerrados += 1
            memoria_liberada += 0.5  # ~0.5 MB por terminal
            print(f"   [OK] PowerShell PID {pid} cerrado")
        except:
            pass
    
    # Cerrar Python
    for pid in procesos_py:
        try:
            subprocess.run(
                ['powershell', '-Command', f'Stop-Process -Id {pid} -Force -ErrorAction SilentlyContinue'],
                capture_output=True,
                timeout=5
            )
            total_cerrados += 1
            memoria_liberada += 10.0  # ~10 MB por proceso Python
            print(f"   [OK] Python PID {pid} cerrado")
        except:
            pass
    
    print()
    print("=" * 70)
    print("RESUMEN DE LIMPIEZA")
    print("=" * 70)
    print(f"Procesos cerrados: {total_cerrados}")
    print(f"Memoria liberada: ~{memoria_liberada:.1f} MB")
    print()
    
    if total_cerrados > 0:
        print("[OK] Limpieza completada exitosamente")
    else:
        print("[INFO] No se encontraron procesos idle para cerrar")
    
    print()
    
    # Mostrar resumen actual
    print("=" * 70)
    print("PROCESOS RESTANTES")
    print("=" * 70)
    
    comando_resumen = """
    Write-Host "PowerShell:" -NoNewline; 
    (Get-Process -Name powershell -ErrorAction SilentlyContinue).Count;
    Write-Host "Python:" -NoNewline; 
    (Get-Process -Name python -ErrorAction SilentlyContinue).Count;
    Write-Host "VS Code:" -NoNewline; 
    (Get-Process -Name Code -ErrorAction SilentlyContinue).Count
    """
    
    try:
        subprocess.run(
            ['powershell', '-Command', comando_resumen],
            timeout=10
        )
    except:
        pass
    
    print()
    print("=" * 70)

if __name__ == '__main__':
    try:
        cerrar_terminales_huerfanos()
    except KeyboardInterrupt:
        print("\n[CANCELADO] Limpieza interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR CRITICO] {e}")
        sys.exit(1)
