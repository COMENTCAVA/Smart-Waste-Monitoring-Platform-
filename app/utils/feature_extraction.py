# app/utils/feature_extraction.py

import os
import numpy as np
from PIL import Image as PILImage
import cv2

def extract_image_features(path: str) -> dict:
    # Ouvre et convertit en RGB
    with PILImage.open(path) as pil:
        pil = pil.convert('RGB')
        arr = np.array(pil)

    # Dimensions & taille disque
    width, height = pil.size
    file_size     = os.path.getsize(path)

    # Moyennes de canaux R, G, B
    avg_color_r = float(np.mean(arr[:,:,0]))
    avg_color_g = float(np.mean(arr[:,:,1]))
    avg_color_b = float(np.mean(arr[:,:,2]))

    # Histogramme niveaux de gris
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    hist_gray, _ = np.histogram(gray, bins=256, range=(0,255))

    # Histogramme de la teinte (H) en HSV
    hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)
    h, _, _ = cv2.split(hsv)
    hist_h, _ = np.histogram(h, bins=180, range=(0,179))

    # Contraste = écart‐type niveaux de gris
    contrast = float(np.std(gray))

    # Comptage des contours
    edges = cv2.Canny(gray, 100, 200)
    edges_count = int(np.count_nonzero(edges))

    # Ratio de pixels sombres (<50)
    total_pix = gray.size
    dark_ratio = int(np.count_nonzero(gray < 50)) / total_pix

    # Occupancy ratio = ratio pixels non‐noirs (>10)
    occupancy_ratio = int(np.count_nonzero(gray > 10)) / total_pix

    return {
        'width':           width,
        'height':          height,
        'file_size':       file_size,
        'avg_color_r':     avg_color_r,
        'avg_color_g':     avg_color_g,
        'avg_color_b':     avg_color_b,
        'hist_gray':       hist_gray.tolist(),
        'hist_h':          hist_h.tolist(),
        'contrast':        contrast,
        'edges_count':     edges_count,
        'dark_ratio':      dark_ratio,
        'occupancy_ratio': occupancy_ratio
    }