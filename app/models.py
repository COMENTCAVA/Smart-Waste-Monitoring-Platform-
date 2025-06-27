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
    hist_r       = db.Column(JSON, nullable=True)    # histogramme R (256 bins)
    hist_g       = db.Column(JSON, nullable=True)    # histogramme G (256 bins)
    hist_b       = db.Column(JSON, nullable=True)    # histogramme B (256 bins)
    hist_gray    = db.Column(JSON, nullable=True)    # histogramme niveaux de gris
    contrast     = db.Column(db.Float, nullable=True)   # contraste = max(gray)-min(gray)
    edges_count  = db.Column(db.Integer, nullable=True) # nombre de contours détectés
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
    key   = db.Column(db.String(50), primary_key=True)  # ex. 'BRIGHTNESS_THRESHOLD'
    value = db.Column(db.Float, nullable=False)         # valeur (float)
