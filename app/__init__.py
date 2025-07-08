# app/__init__.py

from flask import Flask, session, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_babel import Babel, gettext
from flask_login import LoginManager
from sqlalchemy.exc import OperationalError
from config import Config

# ─── Initialisation des extensions ───
db      = SQLAlchemy()
migrate = Migrate()
babel   = Babel()
login_manager = LoginManager()

def recompute_all_predictions():
    from .models import Image
    from .utils.classification_rules import classify_image

    try:
        images = Image.query.all()
    except OperationalError:
        # La BDD n'est pas encore migrée, on quitte silencieusement
        return

    for img in images:
        feats = {
            'avg_color_r':     getattr(img, 'avg_color_r',     0.0),
            'avg_color_g':     getattr(img, 'avg_color_g',     0.0),
            'avg_color_b':     getattr(img, 'avg_color_b',     0.0),
            'file_size':       getattr(img, 'file_size',       0),
            'contrast':        getattr(img, 'contrast',        0),
            'edges_count':     getattr(img, 'edges_count',     0),
            'hist_gray':       getattr(img, 'hist_gray',       None),
            'hist_h':          getattr(img, 'hist_h',          None),
            'occupancy_ratio': getattr(img, 'occupancy_ratio', 0.0),
        }
        img.predicted_label = classify_image(feats)

    db.session.commit()

def get_locale():
    lang = session.get('lang')
    if lang in current_app.config['LANGUAGES']:
        return lang
    return request.accept_languages.best_match(
        current_app.config['LANGUAGES']
    )

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return db.session.get(User, int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ── Internationalisation ──
    app.config['BABEL_DEFAULT_LOCALE']        = 'fr'
    app.config['BABEL_SUPPORTED_LOCALES']     = ['fr', 'en', 'de']
    app.config['LANGUAGES']                   = app.config['BABEL_SUPPORTED_LOCALES']
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

    #Initialisation des extensions
    db.init_app(app)
    migrate.init_app(app, db)
    babel.init_app(app, locale_selector=get_locale)

    # ── Flask-Login ───────────────────────────
    login_manager.init_app(app)
    # page de login par défaut quand @login_required
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'

    # ── Injection dans Jinja ────────────────────
    app.jinja_env.add_extension('jinja2.ext.i18n')

    app.jinja_env.globals.update({
        '_':      gettext,   # pour appeler {{ _('Text') }}
        'gettext':gettext,   # si vous préférez {{ gettext('Text') }}
        'get_locale': get_locale  # pour afficher {{ get_locale() }}
    })

    # ── Enregistrement des blueprints ───────────
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # ── Recompute des prédictions existantes ───────────
    with app.app_context():
        recompute_all_predictions()

    return app