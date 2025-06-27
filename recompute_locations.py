# recompute_locations.py
import os
from app import create_app, db
from app.models import Image
from app.utils.exif_utils import get_exif_latlng

app = create_app()
with app.app_context():
    images_dir = os.path.join(app.root_path, 'static', 'images')
    imgs       = Image.query.all()
    updated    = 0

    print(f"🔍 Found {len(imgs)} image records in the database.\n")

    for idx, img in enumerate(imgs, start=1):
        path = os.path.join(images_dir, img.filename)
        print(f"[{idx}/{len(imgs)}] Processing {img.filename!r}…", end=" ")

        if not os.path.exists(path):
            print("❌ file not found")
            continue

        lat, lon = get_exif_latlng(path)
        if lat is not None and lon is not None:
            img.latitude  = lat
            img.longitude = lon
            db.session.add(img)
            updated += 1
            print(f"✅ gps=({lat:.5f}, {lon:.5f})")
        else:
            print("– no GPS EXIF")

    db.session.commit()
    print(f"\n[✓] Coordonnées EXIF mises à jour pour {updated}/{len(imgs)} images.")