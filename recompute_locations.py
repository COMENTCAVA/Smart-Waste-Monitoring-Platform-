# recompute_locations.py
import os
import random
from app import create_app, db
from app.models import Image
from app.utils.exif_utils import get_exif_latlng

# 1) Définition des « bounding boxes » pour chaque ville
# Format : 'ville': (lat_min, lat_max, lon_min, lon_max)
CITY_BBOXES = {
    # France
    'Paris, FR':       (48.8150, 48.9020,  2.2240,  2.4690),
    'Toulouse, FR':    (43.5400, 43.6700,  1.3600,  1.4900),
    'Lyon, FR':        (45.7120, 45.8000,  4.7600,  4.9000),

    # Amérique du Nord
    'New York, USA':   (40.4774, 40.9176, -74.2591, -73.7004),

    # Asie
    'Tokyo, JP':       (35.5280, 35.8390, 139.4800, 139.9100),

    # Océanie
    'Sydney, AU':      (-34.1183, -33.5780, 150.5200, 151.3430),

    # Amérique du Sud
    'Rio de Janeiro, BR': (-23.0410, -22.7400, -43.7950, -43.0720),

    # Afrique
    'Cape Town, ZA':   (-34.3510, -33.7630,  18.3550,  18.7290),
}

def random_point_in_bbox(bbox):
    """Retourne (lat, lon) aléatoire dans le rectangle bbox."""
    lat_min, lat_max, lon_min, lon_max = bbox
    lat = random.uniform(lat_min, lat_max)
    lon = random.uniform(lon_min, lon_max)
    return lat, lon

app = create_app()

with app.app_context():
    images_dir = os.path.join(app.root_path, 'static', 'images')
    imgs = Image.query.all()
    total = len(imgs)
    exif_count = 0
    random_count = 0

    print(f"🔍 Found {total} image records in the database.\n")

    for idx, img in enumerate(imgs, start=1):
        path = os.path.join(images_dir, img.filename)
        print(f"[{idx}/{total}] Processing {img.filename!r}…", end=" ")

        if not os.path.exists(path):
            print("❌ file not found")
            continue

        # 2) Essai EXIF
        lat, lon = get_exif_latlng(path)
        if lat is not None and lon is not None:
            img.latitude  = lat
            img.longitude = lon
            exif_count += 1
            print(f"✅ EXIF gps=({lat:.5f}, {lon:.5f})")
        else:
            # 3) Aucune EXIF → point aléatoire dans l’une des 3 villes
            city = random.choice(list(CITY_BBOXES.keys()))
            bbox = CITY_BBOXES[city]
            lat, lon = random_point_in_bbox(bbox)
            img.latitude  = lat
            img.longitude = lon
            random_count += 1
            print(f"🎲 Random ({city}) gps=({lat:.5f}, {lon:.5f})")

        db.session.add(img)

    # 4) Sauvegarde en base
    db.session.commit()

    # 5) Rapport final
    print("\n[✓] Summary:")
    print(f"    • EXIF coords updated:      {exif_count}/{total}")
    print(f"    • Random coords assigned:   {random_count}/{total}")
    print(f"    • Total coords in database: {exif_count + random_count}/{total}")