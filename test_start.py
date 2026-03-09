import sys
import subprocess
import os

os.chdir(r"d:\0.1. Backup Equipo Contablilidad\Gestor Documental\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059")

result = subprocess.run(
    [r".venv\Scripts\python.exe", "-c", "import app"],
    capture_output=True, text=True, timeout=30,
    cwd=r"d:\0.1. Backup Equipo Contablilidad\Gestor Documental\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059"
)

with open("logs/test_start_out.txt", "w", encoding="utf-8") as f:
    f.write("=== STDOUT ===\n")
    f.write(result.stdout or "(vacío)\n")
    f.write("=== STDERR ===\n")
    f.write(result.stderr or "(vacío)\n")
    f.write(f"=== EXIT CODE: {result.returncode} ===\n")

print("Done - see logs/test_start_out.txt")
