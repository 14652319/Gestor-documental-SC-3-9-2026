# -*- coding: utf-8 -*-
"""
Verificación simple de columnas
"""
import psycopg2

def verificar_columnas():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="gestor_documental",
            user="postgres",
            password="Inicio2024*"
        )
        cur = conn.cursor()
        
        print("\n" + "="*70)
        print("VERIFICACIÓN FASE 1 - CAMPOS AGREGADOS")
        print("="*70 + "\n")
        
        # Verificar columnas
        cur.execute("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns
            WHERE table_name = 'facturas_digitales'
            AND column_name IN ('departamento', 'forma_pago', 'estado_firma', 
                               'archivo_firmado_path', 'numero_causacion', 'fecha_pago')
            ORDER BY column_name
        """)
        
        resultados = cur.fetchall()
        
        print("📋 CAMPOS NUEVOS EN BASE DE DATOS:")
        print("-" * 70)
        for row in resultados:
            print(f"   ✅ {row[0]}: {row[1]} (default: {row[2] or 'NULL'})")
        
        print(f"\n   Total campos encontrados: {len(resultados)}/6")
        
        print("\n" + "="*70)
        print("✅ FASE 1 COMPLETADA" if len(resultados) == 6 else "⚠️  Faltan campos")
        print("="*70)
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    verificar_columnas()
