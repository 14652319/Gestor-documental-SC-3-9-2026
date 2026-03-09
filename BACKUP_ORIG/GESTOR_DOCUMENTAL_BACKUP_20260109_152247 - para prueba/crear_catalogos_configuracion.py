"""
Script para crear tablas catálogo de configuración
"""
import os
from app import app, db
from modules.configuracion.models import FormaPago, TipoServicio, Departamento

def crear_catalogos():
    """Crea las tablas y datos iniciales"""
    with app.app_context():
        # Crear tablas
        db.create_all()
        print("✅ Tablas creadas/verificadas")
        
        # Formas de Pago
        if FormaPago.query.count() == 0:
            formas = [
                FormaPago(codigo='ESTANDAR', nombre='Estándar', created_by='sistema'),
                FormaPago(codigo='TARJETA_CREDITO', nombre='Tarjeta de Crédito', created_by='sistema')
            ]
            db.session.bulk_save_objects(formas)
            db.session.commit()
            print(f"✅ {len(formas)} Formas de Pago creadas")
        else:
            print(f"ℹ️  Formas de Pago ya existen ({FormaPago.query.count()})")
        
        # Tipos de Servicio
        if TipoServicio.query.count() == 0:
            tipos = [
                TipoServicio(codigo='servicio', nombre='Servicio', created_by='sistema'),
                TipoServicio(codigo='compra', nombre='Compra', created_by='sistema'),
                TipoServicio(codigo='ambos', nombre='Ambos', created_by='sistema')
            ]
            db.session.bulk_save_objects(tipos)
            db.session.commit()
            print(f"✅ {len(tipos)} Tipos de Servicio creados")
        else:
            print(f"ℹ️  Tipos de Servicio ya existen ({TipoServicio.query.count()})")
        
        # Departamentos
        if Departamento.query.count() == 0:
            deptos = [
                Departamento(codigo='FINANCIERO', nombre='Financiero', created_by='sistema'),
                Departamento(codigo='TECNOLOGIA', nombre='Tecnología', created_by='sistema'),
                Departamento(codigo='COMPRAS_Y_SUMINISTROS', nombre='Compras y Suministros', created_by='sistema'),
                Departamento(codigo='MERCADEO', nombre='Mercadeo', created_by='sistema'),
                Departamento(codigo='MVP_ESTRATEGICA', nombre='MVP Estratégica', created_by='sistema'),
                Departamento(codigo='DOMICILIOS', nombre='Domicilios', created_by='sistema')
            ]
            db.session.bulk_save_objects(deptos)
            db.session.commit()
            print(f"✅ {len(deptos)} Departamentos creados")
        else:
            print(f"ℹ️  Departamentos ya existen ({Departamento.query.count()})")
        
        print("\n✅ ¡Catálogos de configuración listos!")

if __name__ == '__main__':
    crear_catalogos()
