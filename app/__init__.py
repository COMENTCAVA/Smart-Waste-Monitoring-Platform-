# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import OperationalError
from config import Config
import app.utils.heif_utils

# Extensions
db = SQLAlchemy()
migrate = Migrate()

def recompute_all_predictions():
    """
    Recalcule predicted_label pour TOUTES les images en base.
    Enrobe dans un try/except pour tolérer l'absence de nouvelles colonnes
    lors des migrations.
    """
    from .models import Image
    from .utils.classification_rules import classify_image

    try:
        imgs = Image.query.all()
    except OperationalError:
        # Schéma pas encore à jour (colonnes manquantes) → on abandonne silencieusement
        return

    for img in imgs:
        feats = {
            'avg_color_r':      getattr(img, 'avg_color_r',      0.0),
            'avg_color_g':      getattr(img, 'avg_color_g',      0.0),
            'avg_color_b':      getattr(img, 'avg_color_b',      0.0),
            'file_size':        getattr(img, 'file_size',        0),
            'contrast':         getattr(img, 'contrast',         0),
            'edges_count':      getattr(img, 'edges_count',      0),
            'hist_gray':        getattr(img, 'hist_gray',        None),
            'hist_h':           getattr(img, 'hist_h',           None),
            'occupancy_ratio':  getattr(img, 'occupancy_ratio',  0.0)
        }
        img.predicted_label = classify_image(feats)

    db.session.commit()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialise les extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Enregistre les blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # ← Ici, on recalcule TOUS les predicted_label (silencieusement si la BDD n'a pas encore
    #      les nouvelles colonnes, grâce au try/except).
    with app.app_context():
        recompute_all_predictions()

    return app