# Generación del ZIP de Entrega TIC

Este archivo explica cómo generar el paquete comprimido con todo el proyecto.

## Ruta de destino
- Se solicitará guardar en: `C:\Users\Usuario\Desktop\Gestor Documental\Documentación\ENTREGA_TIC_SC_GESTOR_DOCUMENTAL.zip`

## Comando PowerShell
```
$src = "C:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059"
$dest = "C:\Users\Usuario\Desktop\Gestor Documental\Documentación\ENTREGA_TIC_SC_GESTOR_DOCUMENTAL.zip"
Compress-Archive -Path $src -DestinationPath $dest -Force
```

## Notas
- Asegúrate de que el entorno virtual `.venv` no haga el ZIP demasiado grande. Si deseas excluirlo, comprime sin la carpeta `.venv`.
- Verifica que existan los archivos `requirements.txt`, `.env.example`, documentación en `docs/`, scripts SQL en `sql/`, y el respaldo de BD en `Backups/`.
