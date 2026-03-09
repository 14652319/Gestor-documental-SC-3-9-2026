# Script para extraer contraseña guardada de Windows Credential Manager
# Servidor: 192.168.11.227

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Text;

namespace CredentialManagement
{
    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    public struct CREDENTIAL
    {
        public int Flags;
        public int Type;
        [MarshalAs(UnmanagedType.LPWStr)]
        public string TargetName;
        [MarshalAs(UnmanagedType.LPWStr)]
        public string Comment;
        public System.Runtime.InteropServices.ComTypes.FILETIME LastWritten;
        public int CredentialBlobSize;
        public IntPtr CredentialBlob;
        public int Persist;
        public int AttributeCount;
        public IntPtr Attributes;
        [MarshalAs(UnmanagedType.LPWStr)]
        public string TargetAlias;
        [MarshalAs(UnmanagedType.LPWStr)]
        public string UserName;
    }

    public class CredentialManager
    {
        [DllImport("advapi32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        public static extern bool CredRead(string target, int type, int reservedFlag, out IntPtr credentialPtr);

        [DllImport("advapi32.dll", SetLastError = true)]
        public static extern bool CredFree(IntPtr cred);

        public static string GetPassword(string target)
        {
            IntPtr credPtr;
            if (CredRead(target, 2, 0, out credPtr)) // Type 2 = CRED_TYPE_DOMAIN_PASSWORD
            {
                CREDENTIAL cred = (CREDENTIAL)Marshal.PtrToStructure(credPtr, typeof(CREDENTIAL));
                byte[] passwordBytes = new byte[cred.CredentialBlobSize];
                Marshal.Copy(cred.CredentialBlob, passwordBytes, 0, cred.CredentialBlobSize);
                string password = Encoding.Unicode.GetString(passwordBytes);
                CredFree(credPtr);
                return password;
            }
            return null;
        }
    }
}
"@

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  EXTRAER CONTRASEÑA DE CREDENCIALES" -ForegroundColor Cyan
Write-Host "  Servidor: 192.168.11.227" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Probar diferentes formatos del target
$targets = @(
    "Domain:target=192.168.11.227",
    "192.168.11.227",
    "TERMSRV/192.168.11.227"
)

Write-Host "Buscando credencial..." -ForegroundColor Gray
$target = $null
$password = $null

foreach ($t in $targets) {
    Write-Host "  Intentando: $t" -ForegroundColor Gray
    try {
        $pwd = [CredentialManagement.CredentialManager]::GetPassword($t)
        if ($pwd) {
            $target = $t
            $password = $pwd
            Write-Host "  ✅ Encontrada!" -ForegroundColor Green
            break
        }
    } catch {
        Write-Host "  ❌ No encontrada" -ForegroundColor Gray
    }
}

Write-Host ""

if ($password) {
    Write-Host "✅ CONTRASEÑA ENCONTRADA:" -ForegroundColor Green
    Write-Host ""
    Write-Host "Target:   $target" -ForegroundColor Yellow
    Write-Host "Servidor: 192.168.11.227" -ForegroundColor Yellow
    Write-Host "Usuario:  supertiendascan\rriascos" -ForegroundColor Yellow
    Write-Host "Password: $password" -ForegroundColor Green -BackgroundColor Black
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "¿Guardar en archivo .txt? (S/N): " -NoNewline
    $respuesta = Read-Host
    
    if ($respuesta -eq "S" -or $respuesta -eq "s") {
        $contenido = @"
CREDENCIALES SERVIDOR DE RED
========================================
Fecha extracción: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

Servidor: \\192.168.11.227\ACREEDORES_DIGITALES
Usuario:  supertiendascan\rriascos
Password: $password

Unidad mapeada: Z:

NOTA: Mantén este archivo seguro y elimínalo después de usar.
"@
        $archivo = "CREDENCIALES_RED_192.168.11.227.txt"
        $contenido | Out-File -FilePath $archivo -Encoding UTF8
        Write-Host "✅ Guardado en: $archivo" -ForegroundColor Green
    }
} else {
    Write-Host "❌ No se pudo leer la contraseña" -ForegroundColor Red
    Write-Host "Posibles causas:" -ForegroundColor Yellow
    Write-Host "  - No tienes permisos de administrador" -ForegroundColor Gray
    Write-Host "  - La credencial está protegida por políticas de grupo" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Presiona Enter para cerrar..."
Read-Host
