# evaluate_model.py

from itertools import product
from app import create_app, recompute_all_predictions, db
from app.models import Setting
from app.utils.classification_rules import DEFAULTS

def ensure_settings():
    for key, default in DEFAULTS.items():
        if not Setting.query.get(key):
            db.session.add(Setting(key=key, value=default))
    db.session.commit()

def compute_accuracy():
    from app.models import Image
    imgs = Image.query.all()
    if not imgs:
        return 0.0
    return sum(1 for img in imgs if img.predicted_label == img.label) / len(imgs)

def grid_search():
    brightness_vals  = [0, 64, 128, 192, 255]
    size_vals        = [50_000, 100_000, 200_000, 500_000]
    contrast_vals    = [10, 40, 80, 120]
    edges_vals       = [100, 500, 1_000, 5_000]
    dark_ratio_vals  = [0.1, 0.3, 0.5, 0.7]
    std_gray_vals    = [20, 40, 60, 80, 100]

    best = {
        'acc': 0.0,
        'B': None, 'S': None, 'C': None,
        'E': None, 'D': None, 'SG': None
    }

    #Boucle sur toutes les combinaisons de 6 seuils
    for B, S, C, E, D, SG in product(
        brightness_vals,
        size_vals,
        contrast_vals,
        edges_vals,
        dark_ratio_vals,
        std_gray_vals
    ):
        Setting.query.filter_by(key='BRIGHTNESS_THRESHOLD').update({'value': B})
        Setting.query.filter_by(key='SIZE_THRESHOLD').update({'value': S})
        Setting.query.filter_by(key='CONTRAST_THRESHOLD').update({'value': C})
        Setting.query.filter_by(key='EDGES_THRESHOLD').update({'value': E})
        Setting.query.filter_by(key='DARK_RATIO_THRESHOLD').update({'value': D})
        Setting.query.filter_by(key='STD_GRAY_THRESHOLD').update({'value': SG})  # ← **Et ici**

        db.session.commit()

        recompute_all_predictions()

        acc = compute_accuracy()
        print(f"Test B={B}, S={S}, C={C}, E={E}, D={D:.1f}, SG={SG} → acc={acc:.2%}")

        if acc > best['acc']:
            best.update(acc=acc, B=B, S=S, C=C, E=E, D=D, SG=SG)

    print("\nMeilleurs seuils trouvés :")
    print(f"  Brightness  = {best['B']}")
    print(f"  File size   = {best['S']}")
    print(f"  Contrast    = {best['C']}")
    print(f"  Edges count = {best['E']}")
    print(f"  Dark ratio  = {best['D']:.1f}")
    print(f"  Std gray    = {best['SG']}")
    print(f"  Accuracy    = {best['acc']:.2%}")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        ensure_settings()
        grid_search()