from app import app

print("\n=== RUTAS REGISTRADAS EN FLASK ===\n")
for rule in app.url_map.iter_rules():
    if 'dian_vs_erp' in str(rule):
        print(f"📍 {rule.endpoint:50s} {rule.rule}")
