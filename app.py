from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'dakar_annonces_secret_2024'

DB = os.path.join(os.path.dirname(__file__), 'instance', 'annonces.db')

CATEGORIES = ['Immobilier', 'Véhicules', 'Électronique', 'Emploi', 'Mode', 'Services', 'Meubles', 'Autres']
REGIONS = ['Dakar', 'Thiès', 'Saint-Louis', 'Ziguinchor', 'Kaolack', 'Touba', 'Mbour', 'Autre']

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                telephone TEXT,
                mot_de_passe TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS annonces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titre TEXT NOT NULL,
                description TEXT NOT NULL,
                prix TEXT NOT NULL,
                categorie TEXT NOT NULL,
                region TEXT NOT NULL,
                etat TEXT DEFAULT 'Neuf',
                urgent INTEGER DEFAULT 0,
                user_id INTEGER,
                telephone TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        ''')
        count = db.execute('SELECT COUNT(*) FROM annonces').fetchone()[0]
        if count == 0:
            exemples = [
                ('Studio meublé Plateau', 'Beau studio entièrement meublé au Plateau, proche de toutes commodités. Eau et électricité comprises.', '350 000 FCFA/mois', 'Immobilier', 'Dakar', 'Neuf', 0, None, '+221 77 123 4567'),
                ('Toyota Corolla 2018', 'Toyota Corolla en très bon état, climatisée, 4 portes, kilométrage faible. Vendu avec carte grise.', '4 500 000 FCFA', 'Véhicules', 'Thiès', 'Occasion', 1, None, '+221 76 234 5678'),
                ('iPhone 13 128Go', 'iPhone 13 en parfait état, batterie 95%, avec boîte originale et chargeur. Débloqué tous opérateurs.', '180 000 FCFA', 'Électronique', 'Dakar', 'Neuf', 0, None, '+221 70 345 6789'),
                ('Comptable expérimenté cherche emploi', 'Comptable avec 5 ans d\'expérience, maîtrise de SAGE et Excel. Disponible immédiatement.', 'Négociable', 'Emploi', 'Dakar', 'Neuf', 0, None, '+221 77 456 7890'),
                ('Canapé 3 places cuir', 'Canapé en cuir véritable, couleur marron, très bon état. Légères traces d\'usure normales.', '85 000 FCFA', 'Meubles', 'Saint-Louis', 'Occasion', 0, None, '+221 76 567 8901'),
                ('Laptop HP Core i5', 'HP Pavilion Core i5, 8Go RAM, 256Go SSD, Windows 11. Parfait pour le bureau ou les études.', '220 000 FCFA', 'Électronique', 'Dakar', 'Occasion', 1, None, '+221 70 678 9012'),
                ('Robe traditionnelle bazin', 'Magnifique robe bazin riche brodée, taille 42, couleur bleue royale. Portée une seule fois.', '45 000 FCFA', 'Mode', 'Dakar', 'Occasion', 0, None, '+221 77 789 0123'),
                ('Plombier professionnel', 'Plombier disponible 7j/7, intervention rapide. Devis gratuit. 10 ans d\'expérience à Dakar.', 'Sur devis', 'Services', 'Dakar', 'Neuf', 0, None, '+221 76 890 1234'),
            ]
            db.executemany(
                'INSERT INTO annonces (titre, description, prix, categorie, region, etat, urgent, user_id, telephone) VALUES (?,?,?,?,?,?,?,?,?)',
                exemples
            )
            db.commit()

@app.route('/')
def index():
    q = request.args.get('q', '')
    categorie = request.args.get('categorie', '')
    region = request.args.get('region', '')
    etat = request.args.get('etat', '')
    tri = request.args.get('tri', 'recent')
    page = int(request.args.get('page', 1))
    par_page = 8

    with get_db() as db:
        sql = 'SELECT * FROM annonces WHERE 1=1'
        params = []
        if q:
            sql += ' AND (titre LIKE ? OR description LIKE ?)'
            params += [f'%{q}%', f'%{q}%']
        if categorie:
            sql += ' AND categorie = ?'
            params.append(categorie)
        if region:
            sql += ' AND region = ?'
            params.append(region)
        if etat:
            sql += ' AND etat = ?'
            params.append(etat)
        if tri == 'recent':
            sql += ' ORDER BY created_at DESC'
        else:
            sql += ' ORDER BY created_at ASC'

        total = db.execute(f'SELECT COUNT(*) FROM ({sql})', params).fetchone()[0]
        offset = (page - 1) * par_page
        annonces = db.execute(sql + f' LIMIT {par_page} OFFSET {offset}', params).fetchall()

    total_pages = (total + par_page - 1) // par_page
    return render_template('index.html',
        annonces=annonces, categories=CATEGORIES, regions=REGIONS,
        q=q, categorie=categorie, region=region, etat=etat, tri=tri,
        page=page, total_pages=total_pages, total=total)

@app.route('/annonce/<int:id>')
def detail(id):
    with get_db() as db:
        annonce = db.execute('SELECT * FROM annonces WHERE id=?', (id,)).fetchone()
    if not annonce:
        return redirect(url_for('index'))
    return render_template('detail.html', annonce=annonce)

@app.route('/publier', methods=['GET', 'POST'])
def publier():
    if request.method == 'POST':
        titre = request.form.get('titre', '').strip()
        description = request.form.get('description', '').strip()
        prix = request.form.get('prix', '').strip()
        categorie = request.form.get('categorie', '')
        region = request.form.get('region', '')
        etat = request.form.get('etat', 'Neuf')
        urgent = 1 if request.form.get('urgent') else 0
        telephone = request.form.get('telephone', '').strip()

        if not all([titre, description, prix, categorie, region, telephone]):
            flash('Veuillez remplir tous les champs obligatoires.', 'danger')
        else:
            with get_db() as db:
                db.execute(
                    'INSERT INTO annonces (titre, description, prix, categorie, region, etat, urgent, telephone) VALUES (?,?,?,?,?,?,?,?)',
                    (titre, description, prix, categorie, region, etat, urgent, telephone)
                )
                db.commit()
            flash('Votre annonce a été publiée avec succès !', 'success')
            return redirect(url_for('index'))
    return render_template('publier.html', categories=CATEGORIES, regions=REGIONS)

@app.route('/supprimer/<int:id>')
def supprimer(id):
    with get_db() as db:
        db.execute('DELETE FROM annonces WHERE id=?', (id,))
        db.commit()
    flash('Annonce supprimée.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
