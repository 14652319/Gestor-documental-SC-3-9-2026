"""
🔧 Script para REMOVER constraint UNIQUE del campo radicado_rfd

Esto es NECESARIO porque:
- Queremos asignar el MISMO radicado a MÚLTIPLES facturas de un lote
- La constraint UNIQUE solo permite un radicado por factura
- Necesitamos cambiar a: UN radicado para MÚLTIPLES facturas

USO:
    python quitar_unique_radicado_rfd.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app, db

def main():
    with app.app_context():
        print("\n" + "="*70)
        print("🔧 QUITAR CONSTRAINT UNIQUE DE radicado_rfd")
        print("="*70)
        
        print("\n📋 Justificación:")
        print("   - Necesitamos asignar UN radicado a MÚLTIPLES facturas de un lote")
        print("   - La constraint UNIQUE lo impide (solo permite 1 radicado = 1 factura)")
        print("   - Solución: Quitar UNIQUE para permitir relación 1:N (1 radicado → N facturas)")
        
        print("\n⚠️  IMPORTANTE: Los radicados aún serán únicos (contador autoincremental)")
        print("   pero MÚLTIPLES facturas podrán compartir el mismo")
        
        respuesta = input("\n¿Ejecutar cambio en BD? (S/N): ").strip().upper()
        
        if respuesta != 'S':
            print("❌ Operación cancelada")
            return
        
        print("\n🔧 Ejecutando ALTER TABLE...")
        
        try:
            # Quitar constraint UNIQUE
            db.session.execute(db.text("""
                ALTER TABLE facturas_digitales 
                DROP CONSTRAINT IF EXISTS facturas_digitales_radicado_rfd_key
            """))
            
            db.session.commit()
            
            print("✅ Constraint UNIQUE removido exitosamente")
            print("\n📊 Ahora puedes asignar el mismo radicado a múltiples facturas")
            print("   Ejemplo: RFD-000004 → FE-445, FE-458, FE-460...")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
