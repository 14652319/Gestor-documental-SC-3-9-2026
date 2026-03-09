"""
extensions.py - Extensiones compartidas de Flask
Solución a importación circular: db se define aquí y se importa en app.py y modules
"""
from flask_sqlalchemy import SQLAlchemy

# Instancia de SQLAlchemy compartida
db = SQLAlchemy()
