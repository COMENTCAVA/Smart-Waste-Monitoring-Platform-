# app/utils/classification_rules.py
import numpy as np
from app import db
from app.models import Setting

#Les seuils par défaut
DEFAULTS = {
    'BRIGHTNESS_THRESHOLD': 127.0,
    'SIZE_THRESHOLD':       100_000.0,
    'CONTRAST_THRESHOLD':   40.0,
    'EDGES_THRESHOLD':      1_000.0,
    'DARK_RATIO_THRESHOLD': 0.30,
    'STD_GRAY_THRESHOLD':   52.70,
    'HUE_RATIO_THRESHOLD':  0.20,
    'OCCUPANCY_THRESHOLD':  0.10
}

def get_threshold(key: str) -> float:
    setting = db.session.get(Setting, key)
    return setting.value if setting else DEFAULTS[key]

def classify_image(features: dict) -> str:
    #Lecture dynamiques des seuils
    B  = get_threshold('BRIGHTNESS_THRESHOLD')
    S  = get_threshold('SIZE_THRESHOLD')
    C  = get_threshold('CONTRAST_THRESHOLD')
    E  = get_threshold('EDGES_THRESHOLD')
    D  = get_threshold('DARK_RATIO_THRESHOLD')
    SG = get_threshold('STD_GRAY_THRESHOLD')
    O = get_threshold('OCCUPANCY_THRESHOLD')
    H = get_threshold('HUE_RATIO_THRESHOLD')

    #Extraction des valeurs
    r, g, b = (
        features.get('avg_color_r', 0.0),
        features.get('avg_color_g', 0.0),
        features.get('avg_color_b', 0.0)
    )
    gray     = (r + g + b) / 3.0
    contrast = features.get('contrast', 0.0)
    edges    = features.get('edges_count', 0)
    hist     = features.get('hist_gray') or []

    #On calcul dark_ratio et std_gray
    if hist and sum(hist):
        total      = sum(hist)
        dark_ratio = sum(hist[:50]) / total
        bins       = np.arange(256)
        vals       = np.array(hist)
        mean       = (bins * vals).sum() / vals.sum()
        var        = ((bins - mean)**2 * vals).sum() / vals.sum()
        std_gray   = np.sqrt(var)
    else:
        dark_ratio = 0.0
        std_gray   = 0.0

    #Enfin on vote sur 5 critères
    votes = 0
    if features.get('file_size', 0) > S and gray < B:
        votes += 1
    if contrast > C:
        votes += 1
    if edges > E:
        votes += 1
    if dark_ratio > D:
        votes += 1
    if std_gray > SG:
        votes += 1


    #Le seuil de vote est :
    return 'Pleine' if votes >= 3 else 'Vide'