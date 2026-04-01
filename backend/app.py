from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import google.generativeai as genai
# test

app = Flask(__name__)
app.secret_key = "cle_secrete_agritech_2026"

# CONFIGURATION IA GEMINI
API_KEY_VALIDE = "AIzaSyCfnUsEQgKyI6fjR8BRks5oSBjSuu1qP4o"
genai.configure(api_key=API_KEY_VALIDE)
model_ai = genai.GenerativeModel('gemini-2.0-flash')

# CONFIGURATION BASE DE DONNÉES (SQLite pour la simplicité locale)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agri_tech.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Utilisateur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20)) # Admin ou Farmer
    analyses = db.relationship('DonneesSol', backref='proprietaire', lazy=True)

class DonneesSol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ph = db.Column(db.Float)
    nitrogen = db.Column(db.Float)
    phosphorus = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'))

with app.app_context():
    db.create_all()
    if not Utilisateur.query.filter_by(email="admin@agri.com").first():
        db.session.add(Utilisateur(nom="Traore Fode", email="admin@agri.com", password="123", role="Admin"))
        db.session.add(Utilisateur(nom="Jean", email="farmer@agri.com", password="456", role="Farmer"))
        db.session.commit()

@app.route('/')
def index(): return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email'); pwd = request.form.get('password')
    user = Utilisateur.query.filter_by(email=email, password=pwd).first()
    if user:
        session.update({'user_id': user.id, 'user_role': user.role, 'user_nom': user.nom})
        return redirect(url_for('dashboard_admin' if user.role == "Admin" else 'dashboard_farmer'))
    flash("Identifiants incorrects."); return redirect(url_for('index'))

@app.route('/dashboard_farmer')
def dashboard_farmer():
    if 'user_id' not in session: return redirect(url_for('index'))
    return render_template('dashboard_farmer.html')

@app.route('/crop_details')
def crop_details():
    if 'user_id' not in session: return redirect(url_for('index'))
    return render_template('crop_details.html')

@app.route('/analyser_sol', methods=['POST'])
def analyser_sol():
    ph = float(request.form.get('ph')); n = float(request.form.get('n')); p = float(request.form.get('p'))
    db.session.add(DonneesSol(ph=ph, nitrogen=n, phosphorus=p, user_id=session['user_id']))
    db.session.commit()
    
    try:
        res = model_ai.generate_content(f"Expert agronome : sol pH {ph}, N {n}, P {p}. Conseil court.")
        conseil = res.text
    except:
        conseil = "🌱 Conseil : pH acide détecté. Ajoutez de la chaux." if ph < 6 else "🌱 Conseil : Sol équilibré."
    return render_template('dashboard_farmer.html', conseil=conseil)

@app.route('/chat', methods=['POST'])
def chat():
    msg = request.get_json().get('message', '')
    try:
        res = model_ai.generate_content("Tu es l'assistant AgriTech. Aide le fermier : " + msg)
        return jsonify({"reponse": res.text})
    except:
        return jsonify({"reponse": "IA indisponible, vérifiez votre quota."})

@app.route('/dashboard_admin')
def dashboard_admin():
    if session.get('user_role') != 'Admin': return redirect(url_for('index'))
    return render_template('dashboard_admin.html', users=Utilisateur.query.all(), analyses=DonneesSol.query.all())

@app.route('/logout')
def logout():
    session.clear(); return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)