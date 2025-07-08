# Smart Waste Monitoring Platform

Ce projet est une plateforme web permettant de surveiller l\'état de bennes à déchets à partir d\'images. Les utilisateurs peuvent téléverser des photos de conteneurs et le système extrait automatiquement différentes caractéristiques pour prédire si la benne est **vide** ou **pleine**. Une interface d\'administration offre des statistiques détaillées ainsi qu\'une carte des dépôts géolocalisés.

## Fonctionnalités

- Téléversement simultané de plusieurs images avec compression automatique.
- Extraction de caractéristiques (taille du fichier, histogrammes, contraste, nombre d\'arêtes, taux de pixels sombres, etc.).
- Classification automatique basée sur des règles ajustables stockées en base de données.
- Tableau de bord affichant les statistiques globales et la précision des prédictions.
- Gestion multilingue (français, anglais, allemand).
- Authentification des utilisateurs avec inscription et connexion.
- API JSON pour récupérer statistiques et images paginées.

## Installation

1. **Cloner le dépôt**
   ```bash
   git clone <url-du-repo>
   cd Smart-Waste-Monitoring-Platform-
   ```
2. **Créer un environnement virtuel** (optionnel mais recommandé)
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```
4. **Initialiser la base de données**
   ```bash
   flask db upgrade
   ```

## Lancement de l\'application

```bash
flask run
```
Par défaut l\'application utilise SQLite (`instance/wdp.db`). Les paramètres principaux se trouvent dans `config.py`.

## Structure du projet

- `app/` – code de l\'application Flask
  - `routes.py` – vues et API
  - `models.py` – définitions des tables SQLAlchemy
  - `forms.py` – formulaires d\'authentification
  - `utils/` – outils d\'extraction de features, règles de classification, etc.
- `migrations/` – scripts de migration de base de données
- `evaluate_features.py` et `evaluate_model_optimized.py` – scripts d\'analyse hors ligne
- `recompute_locations.py` – attribution ou recalcul de coordonnées GPS
- `run.py` – point d\'entrée alternatif pour lancer l\'app

## Optimisation des seuils

La route `/settings/optimize` lance une recherche aléatoire pour déterminer les meilleurs seuils de classification. Les résultats sont enregistrés dans la table `settings` et l\'ensemble des prédictions est alors recalculé.

## API principales

- `/api/images` – renvoie les images paginées et leurs métadonnées
- `/api/stats/overall` – statistiques globales (pourcentage de bennes pleines/vide, précision)
- `/api/stats/*` – autres points de terminaison pour les histogrammes et séries temporelles

Les réponses sont au format JSON et peuvent être utilisées pour créer des tableaux de bord externes.

## Internationalisation

L\'application est livrée avec les traductions françaises par défaut. D\'autres langues peuvent être ajoutées via les outils Flask-Babel (`babel.cfg`, dossier `translations`).

## Licence

Aucune licence explicite n\'est fournie avec ce projet.

