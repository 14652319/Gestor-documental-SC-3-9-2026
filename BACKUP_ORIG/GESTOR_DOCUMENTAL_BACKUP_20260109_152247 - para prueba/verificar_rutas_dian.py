from app import app

print("\n=== RUTAS DIAN VS ERP REGISTRADAS ===\n")
for rule in app.url_map.iter_rules():
    if 'dian_vs_erp' in str(rule):
        methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        print(f"{methods:15s} {rule.rule}")
