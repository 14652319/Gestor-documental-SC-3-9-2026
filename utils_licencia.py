import os
import json
import hashlib
from datetime import datetime, timedelta


def _read_windows_machine_guid():
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Cryptography",
            0,
            winreg.KEY_READ | getattr(winreg, "KEY_WOW64_64KEY", 0),
        )
        value, _ = winreg.QueryValueEx(key, "MachineGuid")
        winreg.CloseKey(key)
        return value or ""
    except Exception:
        return ""


def get_machine_fingerprint() -> str:
    """Genera una huella única de la máquina.

    Preferencias (Windows): MachineGuid + hostname + MAC → SHA256.
    En otras plataformas: hostname + MAC → SHA256.
    """
    try:
        hostname = os.uname().nodename  # type: ignore[attr-defined]
    except Exception:
        import platform
        hostname = platform.node()

    try:
        import uuid
        mac = uuid.getnode()
    except Exception:
        mac = 0

    parts = [str(hostname), str(mac)]
    if os.name == "nt":
        guid = _read_windows_machine_guid()
        if guid:
            parts.insert(0, guid)

    raw = "|".join(parts)
    return hashlib.sha256(raw.encode("utf-8", errors="ignore")).hexdigest()


def _trial_store_dir() -> str:
    # Windows: usar ProgramData si existe; si no, usar carpeta del proyecto
    if os.name == "nt":
        base = os.environ.get("PROGRAMDATA", r"C:\\ProgramData")
        path = os.path.join(base, "GestorDocumental")
    else:
        home = os.path.expanduser("~")
        path = os.path.join(home, ".gestor_documental")
    os.makedirs(path, exist_ok=True)
    return path


def _trial_store_path(fingerprint: str) -> str:
    return os.path.join(_trial_store_dir(), f"trial_{fingerprint[:16]}.json")


def _load_trial_state(fingerprint: str) -> dict:
    p = _trial_store_path(fingerprint)
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_trial_state(fingerprint: str, state: dict) -> None:
    p = _trial_store_path(fingerprint)
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _now_naive():
    # Naive datetime en hora local (consistente con el proyecto)
    return datetime.now().replace(tzinfo=None)


def _parse_bool(value: str, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "t", "yes", "y"}


def _read_int(value: str, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _load_license_file(path: str) -> dict:
    if not path or not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def evaluate_license(app=None) -> dict:
    """Evalúa si la instalación está autorizada.

    Reglas:
    - Si LICENSE_ENFORCE es falso → ok=True.
    - Si hay archivo de licencia y la huella está permitida → ok=True.
    - Si no, entra a periodo de gracia (LICENSE_GRACE_DAYS).
    - Si expira el periodo de gracia → ok=False (motivo='TRIAL_EXPIRED').
    """
    env = os.environ
    enforce = _parse_bool(env.get("LICENSE_ENFORCE", "true"), True)
    license_file = env.get("LICENSE_FILE", "license.lic")
    grace_days = _read_int(env.get("LICENSE_GRACE_DAYS", "180"), 180)
    contact_phone = env.get("LICENSE_CONTACT_PHONE", "")
    cliente_nombre = env.get("LICENSE_CLIENT_NAME", "Supertiendas Cañaveral S.A.S.")

    fingerprint = get_machine_fingerprint()
    info = {
        "ok": True,
        "reason": "AUTHORIZED",
        "days_left": None,
        "fingerprint": fingerprint,
        "contact_phone": contact_phone,
        "client_name": cliente_nombre,
    }

    if not enforce:
        return info

    lic = _load_license_file(license_file)
    allowed = set(lic.get("allowed_fingerprints", []) or [])

    if fingerprint in allowed:
        # Instalación autorizada
        return info

    # No autorizado → periodo de gracia
    state = _load_trial_state(fingerprint)
    now = _now_naive()
    if not state.get("first_seen"):
        state["first_seen"] = now.isoformat(timespec="seconds")
        state["last_seen"] = state["first_seen"]
        _save_trial_state(fingerprint, state)

    else:
        state["last_seen"] = now.isoformat(timespec="seconds")
        _save_trial_state(fingerprint, state)

    try:
        first_seen = datetime.fromisoformat(state["first_seen"])  # naive
    except Exception:
        first_seen = now

    elapsed = (now - first_seen).days
    remaining = max(0, grace_days - elapsed)

    if elapsed >= grace_days:
        info.update({
            "ok": False,
            "reason": "TRIAL_EXPIRED",
            "days_left": 0,
        })
    else:
        info.update({
            "ok": True,
            "reason": "TRIAL",
            "days_left": remaining,
        })

    return info


def build_license_notice_html(status: dict) -> str:
    phone = status.get("contact_phone") or ""
    client = status.get("client_name") or "Supertiendas Cañaveral S.A.S."
    fp = status.get("fingerprint") or ""
    days_left = status.get("days_left")
    trial_msg = ""
    if status.get("reason") == "TRIAL" and days_left is not None:
        trial_msg = f"<p style='margin:8px 0;color:#444'>Quedan <b>{days_left} días</b> del periodo de gracia no autorizado.</p>"

    phone_block = (
        f"<p style='margin:8px 0'>Por favor comunicarse con el desarrollador para subsanar este inconveniente. Teléfono: <b>{phone}</b></p>"
        if phone else ""
    )

    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Licencia no autorizada</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; background:#f8fafc; margin:0; }}
    .wrap {{ max-width:760px; margin:40px auto; background:#fff; border-radius:12px; box-shadow:0 6px 20px rgba(0,0,0,.08); overflow:hidden; }}
    .header {{ background:linear-gradient(145deg,#e11d48,#be123c); color:#fff; padding:28px 32px; }}
    .content {{ padding:28px 32px; color:#0f172a; }}
    .badge {{ display:inline-block; background:#fee2e2; color:#991b1b; border:1px solid #fecaca; padding:4px 10px; border-radius:999px; font-weight:600; font-size:12px; letter-spacing:.3px; }}
    code {{ background:#f1f5f9; border:1px solid #e2e8f0; border-radius:6px; padding:2px 6px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
    .footer {{ padding:18px 32px; border-top:1px solid #e5e7eb; color:#334155; font-size:14px; }}
    a.btn {{ display:inline-block; background:#0ea5e9; color:#fff; padding:10px 14px; border-radius:8px; text-decoration:none; margin-top:10px; }}
  </style>
  <meta http-equiv="refresh" content="60" />
  <script>setTimeout(()=>location.reload(), 60000)</script>
  </head>
<body>
  <div class="wrap">
    <div class="header">
      <div class="badge">LICENCIA NO AUTORIZADA</div>
      <h1 style="margin:10px 0 0; font-weight:800;">Esta instalación no está autorizada para este servidor</h1>
    </div>
    <div class="content">
      <p>Este software fue diseñado para <b>{client}</b>. La copia en uso no está autorizada para este equipo o servidor.</p>
      {trial_msg}
      <p style="margin:8px 0">Huella del servidor: <code>{fp}</code></p>
      {phone_block}
      <p style="margin:16px 0 0;color:#475569">Si ya cuenta con licencia válida, coloque el archivo <code>license.lic</code> en la carpeta del sistema o configure la variable <code>LICENSE_FILE</code>.</p>
      <a class="btn" href="/">Volver al inicio</a>
    </div>
    <div class="footer">
      <p>Para habilitar definitivamente esta instalación, emita una licencia asociada a esta huella y actualice el servidor. Este mensaje se actualizará automáticamente.</p>
    </div>
  </div>
</body>
</html>
"""
