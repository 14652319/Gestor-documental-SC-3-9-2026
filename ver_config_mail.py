"""
Verificar configuración de correo en Flask
"""
from app import app

print("\n" + "="*80)
print("🔍 CONFIGURACIÓN DE CORREO EN FLASK")
print("="*80)

with app.app_context():
    print(f"\n📧 Variables de configuración:")
    print(f"  ├─ MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
    print(f"  ├─ MAIL_PORT: {app.config.get('MAIL_PORT')}")
    print(f"  ├─ MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
    print(f"  ├─ MAIL_USE_SSL: {app.config.get('MAIL_USE_SSL')}")
    print(f"  ├─ MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
    password = app.config.get('MAIL_PASSWORD')
    print(f"  ├─ MAIL_PASSWORD: {'*' * len(password) if password else 'NO CONFIGURADO'}")
    print(f"  └─ MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
    
    print(f"\n✅ Configuración actual:")
    if app.config.get('MAIL_USE_SSL'):
        print(f"   Modo: SSL (Puerto {app.config.get('MAIL_PORT')})")
    elif app.config.get('MAIL_USE_TLS'):
        print(f"   Modo: TLS (Puerto {app.config.get('MAIL_PORT')})")
    else:
        print(f"   Modo: Sin cifrado (Puerto {app.config.get('MAIL_PORT')})")

print("\n" + "="*80)
