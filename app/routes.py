# app/routes.py

import os
from datetime import datetime

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, current_app, flash, jsonify
)

from . import db
from .models import Image, Setting
from .utils.exif_utils import get_exif_latlng
from .utils.feature_extraction import extract_image_features
from .utils.classification_rules import classify_image, DEFAULTS
from .utils.image_utils import compress_image

main_bp = Blueprint('main', __name__)

from flask import (
    session, request, redirect, url_for, current_app, abort
)


# ─── Système de multi-langue ───

@main_bp.route('/lang/<lang_code>')
def set_language(lang_code):
    if lang_code not in current_app.config['LANGUAGES']:
        abort(404)
    session['lang'] = lang_code
    return redirect(request.referrer or url_for('main.home'))

# ────────────────────────────────

@main_bp.route('/', methods=['GET'])
def home():
    return render_template('upload.html')

@main_bp.route('/map', methods=['GET'])
def map_view():
    """Affiche la carte EXIF-géolocalisée."""
    return render_template('map.html')

@main_bp.route('/upload', methods=['POST'])
def upload():
    # 1) Récupère tous les fichiers sélectionnés et le label
    files = request.files.getlist('images')
    label = request.form.get('label')  # 'Vide' ou 'Pleine'
    if not files or label not in ('Vide', 'Pleine'):
        flash("Veuillez choisir au moins une image et un état.", 'error')
        return redirect(url_for('main.home'))

    # 2) Prépare le dossier de stockage
    images_dir = os.path.join(current_app.root_path, 'static', 'images')
    os.makedirs(images_dir, exist_ok=True)

    count = 0
    for file in files:
        if not file or file.filename == '':
            continue

        filename = file.filename
        save_path = os.path.join(images_dir, filename)

        # 3) Sauvegarde du fichier original
        file.save(save_path)

        # 4) Compression JPEG (optimize + quality)
        compress_image(save_path, quality=85)
        lat, lng = get_exif_latlng(save_path)

        # 5) Création ou récupération de l’enregistrement
        img = Image.query.filter_by(filename=filename).first()
        if not img:
            img = Image(filename=filename)
            db.session.add(img)

            img.latitude = lat
            img.longitude = lng

        # 6) Extraction des features (file_size mis à jour après compression)
        features = extract_image_features(save_path)
        for key, val in features.items():
            setattr(img, key, val)

        # 7) Labels manuel + automatique
        img.label = label
        img.predicted_label = classify_image(features)
        count += 1

    # 8) Persiste toutes les modifications en une seule transaction
    db.session.commit()

    flash(
        f"{count} image(s) traitée(s) – compression + annotation réussie.",
        'success'
    )
    return redirect(url_for('main.dashboard'))

import threading, random
from flask import jsonify
from evaluate_model_optimized import classify_batch, load_data
from app.models import Setting
from . import db
from app import recompute_all_predictions
from app.utils.classification_rules import DEFAULTS

@main_bp.route('/settings/optimize', methods=['POST'])
def optimize_settings():
    """
    Lance en arrière-plan la recherche aléatoire des meilleurs seuils,
    met à jour la table Setting, et relance recompute_all_predictions().
    """
    def worker():
        df = load_data()
        N_TRIALS = 100_000
        best = {'acc': 0.0}
        for _ in range(N_TRIALS):
            B  = random.uniform(0,   255)
            S  = random.uniform(50e3, 500e3)
            C  = random.uniform(0,   200)
            E  = random.uniform(100, 50e3)
            D  = random.uniform(0.1, 0.7)
            SG = random.uniform(0,  300)
            acc = classify_batch(df, B, S, C, E, D, SG)
            if acc > best['acc']:
                best.update(acc=acc, B=B, S=S, C=C, E=E, D=D, SG=SG)

        # mise à jour en base
        keys = [
            'BRIGHTNESS_THRESHOLD', 'SIZE_THRESHOLD', 'CONTRAST_THRESHOLD',
            'EDGES_THRESHOLD', 'DARK_RATIO_THRESHOLD', 'STD_GRAY_THRESHOLD'
        ]
        vals = [best['B'], best['S'], best['C'], best['E'], best['D'], best['SG']]
        for key, val in zip(keys, vals):
            setting = Setting.query.get(key)
            if setting:
                setting.value = val
            else:
                db.session.add(Setting(key=key, value=val))
        db.session.commit()
        recompute_all_predictions()

    threading.Thread(target=worker, daemon=True).start()
    return jsonify(success=True)

@main_bp.route('/dashboard', methods=['GET'])
def dashboard():
    records = Image.query.order_by(Image.uploaded_at.desc()).all()
    total = len(records)

    # Statistiques labels manuels
    manual_empty = sum(1 for img in records if img.label == 'Vide')
    manual_full = sum(1 for img in records if img.label == 'Pleine')
    manual_empty_pct = (manual_empty / total * 100) if total else 0
    manual_full_pct = (manual_full / total * 100) if total else 0

    # Précision des prédictions automatiques
    correct = sum(
        1 for img in records
        if img.predicted_label and img.predicted_label == img.label
    )
    correct_pct = (correct / total * 100) if total else 0

    return render_template(
        'dashboard.html',
        images=records,
        total=total,
        manual_empty=manual_empty,
        manual_full=manual_full,
        manual_empty_pct=manual_empty_pct,
        manual_full_pct=manual_full_pct,
        correct=correct,
        correct_pct=correct_pct
    )


@main_bp.route('/delete/<int:image_id>', methods=['POST'])
def delete_image(image_id):
    img = Image.query.get_or_404(image_id)

    # Suppression du fichier sur le disque
    file_path = os.path.join(
        current_app.root_path, 'static', 'images', img.filename
    )
    if os.path.exists(file_path):
        os.remove(file_path)

    # Suppression de l'enregistrement en base
    db.session.delete(img)
    db.session.commit()

    flash(f"L'image « {img.filename} » a bien été supprimée.", 'success')
    return redirect(url_for('main.dashboard'))


@main_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # Enregistre chaque seuil
        for key in DEFAULTS.keys():
            val = request.form.get(key)
            try:
                fval = float(val)
            except (TypeError, ValueError):
                continue
            setting = Setting.query.get(key)
            if setting:
                setting.value = fval
            else:
                db.session.add(Setting(key=key, value=fval))

        db.session.commit()

        # Recalcule immédiatement toutes les prédictions
        from app import recompute_all_predictions
        recompute_all_predictions()

        flash("Seuils mis à jour et prédictions recalculées.", 'success')
        return redirect(url_for('main.settings'))

    # GET : charge les valeurs existantes ou défaut
    data = {}
    for key, default in DEFAULTS.items():
        setting = Setting.query.get(key)
        data[key] = setting.value if setting else default

    return render_template('settings.html', settings=data)


import tempfile
@main_bp.route('/api/extract_features', methods=['POST'])
def api_extract_features():
    img = request.files.get('image')
    if not img:
        return jsonify({"error": "No image provided"}), 400

    suffix = os.path.splitext(img.filename)[1]
    tmpf = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    img.save(tmpf.name)
    tmpf.close()

    features = extract_image_features(tmpf.name)

    os.unlink(tmpf.name)

    return jsonify(features)


# ──────────────────────────────────────────────────────────────────────────────
# APIs pour les stats et images paginées

@main_bp.route('/api/stats/label_distribution')
def api_label_distribution():
    manual_vide = Image.query.filter_by(label='Vide').count()
    manual_pleine = Image.query.filter_by(label='Pleine').count()
    auto_vide = Image.query.filter_by(predicted_label='Vide').count()
    auto_pleine = Image.query.filter_by(predicted_label='Pleine').count()
    return jsonify({
        'manual':   {'Vide': manual_vide,   'Pleine': manual_pleine},
        'automatic':{'Vide': auto_vide,     'Pleine': auto_pleine}
    })


@main_bp.route('/api/stats/file_size_distribution')
def api_file_size_distribution():
    bins = [0, 50_000, 100_000, 200_000, 500_000, float('inf')]
    labels = ['0–50 k', '50–100 k', '100–200 k', '200–500 k', '> 500 k']
    counts = []
    for i in range(len(bins)-1):
        lo, hi = bins[i], bins[i+1]
        if hi == float('inf'):
            cnt = Image.query.filter(Image.file_size > lo).count()
        else:
            cnt = Image.query.filter(
                Image.file_size >= lo,
                Image.file_size < hi
            ).count()
        counts.append(cnt)
    return jsonify({'labels': labels, 'counts': counts})


@main_bp.route('/api/stats/contrast_distribution')
def api_contrast_distribution():
    edges = list(range(0, 301, 50)) + [float('inf')]
    labels = [
        f'{edges[i]}–{edges[i+1]}' for i in range(len(edges)-2)
    ] + ['> 300']
    counts = []
    for i in range(len(edges)-1):
        lo, hi = edges[i], edges[i+1]
        if hi == float('inf'):
            cnt = Image.query.filter(Image.contrast > lo).count()
        else:
            cnt = Image.query.filter(
                Image.contrast >= lo,
                Image.contrast < hi
            ).count()
        counts.append(cnt)
    return jsonify({'labels': labels, 'counts': counts})


@main_bp.route('/api/stats/edges_distribution')
def api_edges_distribution():
    edges = [0, 1_000, 5_000, 10_000, 20_000, 50_000, float('inf')]
    labels = ['0–1 k', '1–5 k', '5–10 k', '10–20 k', '20–50 k', '> 50 k']
    counts = []
    for i in range(len(edges)-1):
        lo, hi = edges[i], edges[i+1]
        if hi == float('inf'):
            cnt = Image.query.filter(Image.edges_count > lo).count()
        else:
            cnt = Image.query.filter(
                Image.edges_count >= lo,
                Image.edges_count < hi
            ).count()
        counts.append(cnt)
    return jsonify({'labels': labels, 'counts': counts})


@main_bp.route('/api/images')
def api_images():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 21, type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    manual_lbl = request.args.get('label_manual')
    auto_lbl = request.args.get('label_auto')

    query = Image.query
    if date_from:
        df = datetime.fromisoformat(date_from)
        query = query.filter(Image.uploaded_at >= df)
    if date_to:
        dt = datetime.fromisoformat(date_to)
        query = query.filter(Image.uploaded_at <= dt)
    if manual_lbl:
        query = query.filter(Image.label == manual_lbl)
    if auto_lbl:
        query = query.filter(Image.predicted_label == auto_lbl)

    pagination = query.order_by(
        Image.uploaded_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for img in pagination.items:
        items.append({
            'id': img.id,
            'filename': img.filename,
            'url': url_for(
                'static', filename='images/'+img.filename
            ),
            'label': img.label,
            'predicted_label': img.predicted_label,
            'uploaded_at': img.uploaded_at.isoformat(),
            'file_size': img.file_size,
            'contrast': img.contrast,
            'edges_count': img.edges_count,
            'latitude': img.latitude,
            'longitude': img.longitude
        })

    return jsonify({'images': items, 'has_next': pagination.has_next})


@main_bp.route('/api/stats/overall')
def api_stats_overall():
    records = Image.query.all()
    total = len(records)
    manual_empty = sum(1 for img in records if img.label == 'Vide')
    manual_full = sum(1 for img in records if img.label == 'Pleine')
    correct = sum(1 for img in records if img.predicted_label == img.label)
    return jsonify({
        'total': total,
        'manual_empty_pct': round(manual_empty/total*100, 1) if total else 0,
        'manual_full_pct': round(manual_full/total*100, 1) if total else 0,
        'correct_pct': round(correct/total*100, 1) if total else 0
    })