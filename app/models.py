# app/models.py
from datetime import datetime
from . import db
from sqlalchemy import JSON

class Image(db.Model):
    __tablename__ = 'images'

    id           = db.Column(db.Integer, primary_key=True)
    filename     = db.Column(db.String(255), nullable=False, unique=True)
    uploaded_at  = db.Column(db.DateTime, default=datetime.utcnow)

    # Caractéristiques de base
    width        = db.Column(db.Integer, nullable=True)
    height       = db.Column(db.Integer, nullable=True)
    file_size    = db.Column(db.Integer, nullable=True)
    avg_color_r  = db.Column(db.Float,   nullable=True)
    avg_color_g  = db.Column(db.Float,   nullable=True)
    avg_color_b  = db.Column(db.Float,   nullable=True)

    # Label manuel / automatique
    label        = db.Column(db.String(50), nullable=True)
    predicted_label = db.Column(db.String(50), nullable=True)

    # Nouveaux attributs pour extraction avancée
    hist_r       = db.Column(JSON, nullable=True)
    hist_g       = db.Column(JSON, nullable=True)
    hist_b       = db.Column(JSON, nullable=True)
    hist_gray    = db.Column(JSON, nullable=True)
    contrast     = db.Column(db.Float, nullable=True)
    edges_count  = db.Column(db.Integer, nullable=True)
    hist_h = db.Column(db.JSON, nullable=True)
    occupancy_ratio = db.Column(db.Float, nullable=True)

    # Géolocalisation extraite des EXIF
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

class Setting(db.Model):
    """
    Stocke une paire (key, value) pour paramétrer les seuils
    utilisées par classify_image().
    """
    __tablename__ = 'settings'
    key   = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.Float, nullable=False)

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id           = db.Column(db.Integer, primary_key=True)
    username     = db.Column(db.String(64), unique=True, nullable=False)
    email        = db.Column(db.String(120), unique=True, nullable=False)
    password_hash= db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(
            password, method='pbkdf2:sha256', salt_length=16
        )

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
