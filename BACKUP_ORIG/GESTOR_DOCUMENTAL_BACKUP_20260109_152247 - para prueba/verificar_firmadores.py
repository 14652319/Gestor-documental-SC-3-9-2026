"""
Script para verificar configuración de firmadores por departamento
Verifica que cada departamento tenga al menos un firmador activo
"""

import sys
from app import app, db
from sqlalchemy import text

def main():
    with app.app_context():
        print("\n" + "=" * 80)
        print("🔍 VERIFICACIÓN DE FIRMADORES POR DEPARTAMENTO")
        print("=" * 80)
        
        # Query para obtener firmadores activos por departamento
        query = text("""
            SELECT 
                udf.departamento,
                COUNT(*) as total_firmadores,
                STRING_AGG(u.usuario, ', ') as usuarios,
                STRING_AGG(COALESCE(u.email_notificaciones, u.email, u.correo), ', ') as emails
            FROM usuario_departamento_firma udf
            JOIN usuarios u ON u.id = udf.usuario_id
            WHERE udf.es_firmador = true 
              AND udf.activo = true
            GROUP BY udf.departamento
            ORDER BY udf.departamento
        """)
        
        try:
            result = db.session.execute(query)
            firmadores = result.fetchall()
            
            if not firmadores:
                print("\n❌ NO HAY FIRMADORES CONFIGURADOS EN EL SISTEMA")
                print("\n📝 Necesitas configurar firmadores en la tabla 'usuario_departamento_firma'")
                print("   Cada registro debe tener:")
                print("   - usuario_id: ID del usuario firmador")
                print("   - departamento: TIC, MER, FIN, DOM, MYP")
                print("   - es_firmador: true")
                print("   - activo: true")
                return
            
            print(f"\n✅ Se encontraron firmadores en {len(firmadores)} departamento(s)\n")
            
            departamentos_validos = {'TIC', 'MER', 'FIN', 'DOM', 'MYP'}
            departamentos_encontrados = set()
            
            for depto, total, usuarios, emails in firmadores:
                departamentos_encontrados.add(depto)
                
                print(f"📂 DEPARTAMENTO: {depto}")
                print(f"   👥 Firmadores activos: {total}")
                print(f"   👤 Usuarios: {usuarios}")
                print(f"   📧 Emails: {emails}")
                print()
            
            # Verificar departamentos faltantes
            faltantes = departamentos_validos - departamentos_encontrados
            if faltantes:
                print("\n⚠️ ADVERTENCIA: Departamentos SIN firmadores asignados:")
                for dept in sorted(faltantes):
                    print(f"   ❌ {dept}")
                print("\n   Las facturas de estos departamentos NO podrán enviarse a firmar")
            else:
                print("\n✅ TODOS los departamentos tienen firmadores asignados")
            
            # Verificar emails
            print("\n" + "-" * 80)
            print("🔍 VERIFICACIÓN DE EMAILS")
            print("-" * 80)
            
            query_emails = text("""
                SELECT 
                    u.usuario,
                    udf.departamento,
                    COALESCE(u.email_notificaciones, u.email, u.correo, 'SIN EMAIL') as email_final
                FROM usuario_departamento_firma udf
                JOIN usuarios u ON u.id = udf.usuario_id
                WHERE udf.es_firmador = true 
                  AND udf.activo = true
                ORDER BY udf.departamento, u.usuario
            """)
            
            result = db.session.execute(query_emails)
            usuarios_emails = result.fetchall()
            
            sin_email = []
            con_email = []
            
            for usuario, depto, email in usuarios_emails:
                if email == 'SIN EMAIL':
                    sin_email.append((usuario, depto))
                    print(f"   ❌ {usuario} ({depto}): SIN EMAIL CONFIGURADO")
                else:
                    con_email.append((usuario, depto, email))
                    print(f"   ✅ {usuario} ({depto}): {email}")
            
            print("\n" + "=" * 80)
            print("📊 RESUMEN")
            print("=" * 80)
            print(f"   ✅ Firmadores con email: {len(con_email)}")
            print(f"   ❌ Firmadores sin email: {len(sin_email)}")
            print(f"   📂 Departamentos configurados: {len(firmadores)}")
            print(f"   ⚠️ Departamentos faltantes: {len(faltantes)}")
            
            if sin_email:
                print("\n❌ ACCIÓN REQUERIDA:")
                print("   Los siguientes usuarios necesitan configurar un email:")
                for usuario, depto in sin_email:
                    print(f"   • {usuario} ({depto})")
                print("\n   Actualiza la tabla 'usuarios' agregando:")
                print("   - Campo 'email' o")
                print("   - Campo 'email_notificaciones' o")
                print("   - Campo 'correo'")
            
            print("\n" + "=" * 80)
            
            if sin_email or faltantes:
                print("⚠️ ESTADO: Sistema parcialmente configurado")
                print("   Algunas facturas NO podrán enviarse por falta de firmadores/emails")
            else:
                print("✅ ESTADO: Sistema completamente configurado")
                print("   Todos los departamentos tienen firmadores con emails válidos")
            
            print("=" * 80 + "\n")
            
        except Exception as e:
            print(f"\n❌ ERROR al consultar base de datos:")
            print(f"   {str(e)}")
            print("\n💡 Posibles causas:")
            print("   1. La tabla 'usuario_departamento_firma' no existe")
            print("   2. La estructura de tablas es diferente")
            print("   3. Error de conexión a la base de datos")
            
            # Intentar crear la tabla si no existe
            print("\n🔧 Intentando verificar estructura de tablas...")
            
            try:
                query_tablas = text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                      AND table_name IN ('usuarios', 'usuario_departamento_firma')
                """)
                result = db.session.execute(query_tablas)
                tablas = [row[0] for row in result]
                
                print(f"\n✅ Tablas encontradas: {', '.join(tablas)}")
                
                if 'usuario_departamento_firma' not in tablas:
                    print("\n❌ La tabla 'usuario_departamento_firma' NO EXISTE")
                    print("   Esta tabla es necesaria para el sistema de envío masivo")
                    print("\n📝 SQL para crear la tabla:")
                    print("""
CREATE TABLE usuario_departamento_firma (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    departamento VARCHAR(10) NOT NULL,
    es_firmador BOOLEAN DEFAULT true,
    activo BOOLEAN DEFAULT true,
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(usuario_id, departamento)
);

-- Ejemplo de inserción:
INSERT INTO usuario_departamento_firma (usuario_id, departamento, es_firmador, activo)
VALUES 
    (1, 'TIC', true, true),  -- Usuario ID 1 firmador de TIC
    (2, 'MER', true, true),  -- Usuario ID 2 firmador de MER
    (3, 'FIN', true, true);  -- Usuario ID 3 firmador de FIN
                    """)
            except Exception as e2:
                print(f"\n❌ Error adicional: {e2}")

if __name__ == "__main__":
    main()
