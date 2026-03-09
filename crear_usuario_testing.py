"""
Crea usuario específico para testing de carga de archivos
"""
from app import app, db, Usuario, Tercero
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

with app.app_context():
    # Buscar o crear tercero
    tercero = Tercero.query.filter_by(nit='805028041').first()
    if not tercero:
        tercero = Tercero(
            nit='805028041',
            razon_social='Supertiendas Cañaveral',
            tipo_persona='juridica',
            correo='testing@example.com'
        )
        db.session.add(tercero)
        db.session.flush()
    
    # Buscar o actualizar usuario
    usuario = Usuario.query.filter_by(usuario='test_upload').first()
    
    password = 'TestUpload2024*'
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    
    if usuario:
        usuario.password_hash = hashed
        usuario.activo = True
        print(f"✅ Usuario 'test_upload' actualizado")
    else:
        usuario = Usuario(
            tercero_id=tercero.id,
            usuario='test_upload',
            password_hash=hashed,
            correo='testing@example.com',
            activo=True,
            rol='interno'
        )
        db.session.add(usuario)
        print(f"✅ Usuario 'test_upload' creado")
    
    db.session.commit()
    
    print(f"""
========================================
USUARIO DE TESTING CREADO
========================================
NIT: 805028041
Usuario: test_upload
Password: {password}
========================================
""")
