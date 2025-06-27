# app/utils/exif_utils.py

import pillow_heif
pillow_heif.register_heif_opener()

from PIL import Image as PILImage
from PIL.ExifTags import TAGS, GPSTAGS

def _to_degrees(value):
    """
    Transforme une séquence DMS EXIF en degrés décimaux.
    Supporte à la fois :
     - un tuple de tuples ((num,den), …)
     - des objets IFDRational (float(x) fonctionne)
    """
    def to_float(x):
        # x peut être (num,den) ou IFDRational
        try:
            return x[0] / x[1]
        except Exception:
            return float(x)
    d, m, s = value
    return to_float(d) + to_float(m) / 60.0 + to_float(s) / 3600.0

def get_exif_latlng(path: str):
    """
    Lit les tags GPS d’une image et renvoie (lat, lon) en décimal,
    ou (None, None) si ABSOLUMENT aucune info GPS.
    """
    try:
        img = PILImage.open(path)
        exif = img._getexif() or {}
        if exif:
            print("for path " + path)
            print("→ EXIF keys trouvées :", list(exif.keys()))
    except Exception:
        return None, None

    gps_info = {}
    for tag_id, val in exif.items():
        tag = TAGS.get(tag_id, tag_id)
        if tag == "GPSInfo":
            for key, v in val.items():
                sub = GPSTAGS.get(key, key)
                gps_info[sub] = v

    lat = gps_info.get("GPSLatitude")
    lat_ref = gps_info.get("GPSLatitudeRef")
    lon = gps_info.get("GPSLongitude")
    lon_ref = gps_info.get("GPSLongitudeRef")

    if lat and lat_ref and lon and lon_ref:
        try:
            lat_deg = _to_degrees(lat)
            if lat_ref.upper() == "S":
                lat_deg = -lat_deg
            lon_deg = _to_degrees(lon)
            if lon_ref.upper() == "W":
                lon_deg = -lon_deg
            return lat_deg, lon_deg
        except Exception:
            return None, None

    return None, None