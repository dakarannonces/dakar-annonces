# DakarAnnonces 🇸🇳
Site de petites annonces pour le Sénégal — développé avec Python Flask

## Installation

### 1. Installer Python (si pas déjà installé)
Télécharger sur https://python.org

### 2. Installer Flask
```bash
pip install flask
```

### 3. Lancer le site
```bash
cd dakar_annonces
python app.py
```

### 4. Ouvrir dans le navigateur
```
http://localhost:5000
```

## Fonctionnalités
- ✅ Page d'accueil avec toutes les annonces
- ✅ Recherche par mot-clé
- ✅ Filtres par catégorie, région, état
- ✅ Page de détail de chaque annonce
- ✅ Formulaire pour publier une annonce
- ✅ Bouton WhatsApp pour contacter le vendeur
- ✅ Suppression d'annonces
- ✅ Base de données SQLite (aucune config nécessaire)
- ✅ Annonces exemples pré-chargées au démarrage

## Structure du projet
```
dakar_annonces/
├── app.py              # Application principale
├── instance/
│   └── annonces.db     # Base de données (créée automatiquement)
└── templates/
    ├── base.html       # Template de base
    ├── index.html      # Page d'accueil
    ├── detail.html     # Détail d'une annonce
    └── publier.html    # Formulaire de publication
```

## Catégories disponibles
Immobilier, Véhicules, Électronique, Emploi, Mode, Services, Meubles, Autres

## Régions disponibles
Dakar, Thiès, Saint-Louis, Ziguinchor, Kaolack, Touba, Mbour, Autre
