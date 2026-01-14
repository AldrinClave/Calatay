import os
import uuid
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- DATABASE CONFIG ---
database_url = os.getenv("DATABASE_URL") or os.getenv("MYSQL_URL")

if database_url and database_url.startswith("mysql://"):
    database_url = database_url.replace("mysql://", "mysql+pymysql://", 1)

# Fallback for local dev
if not database_url:
    database_url = "sqlite:///gamer_system.db"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# --- MODEL ---
class Gamer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    favorite_game = db.Column(db.String(120), nullable=False)
    platform = db.Column(db.String(50))
    region = db.Column(db.String(50))
    rank = db.Column(db.String(50), nullable=False)

# --- AUTO CREATE TABLES (GUNICORN SAFE) ---
with app.app_context():
    db.create_all()

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('register.html')

@app.route('/submit', methods=['POST'])
def submit():
    username = request.form.get('username')
    game = request.form.get('favorite_game')
    rank = request.form.get('rank')
    platform = request.form.get('platform')
    region = request.form.get('region')

    agent_id = f"MG-{uuid.uuid4().hex[:8].upper()}"
    identity = f"{agent_id} | {username}"

    gamer = Gamer(
        username=identity,
        favorite_game=game,
        rank=rank,
        platform=platform,
        region=region
    )

    db.session.add(gamer)
    db.session.commit()

    return redirect(url_for('gamers'))

@app.route('/gamers')
def gamers():
    rows = Gamer.query.order_by(Gamer.id.desc()).all()
    return render_template('gamers.html', gamers=rows)

# --- DELETE SINGLE (POST ONLY) ---
@app.route('/delete/<int:id>', methods=['POST'])
def delete_gamer(id):
    gamer = Gamer.query.get_or_404(id)
    db.session.delete(gamer)
    db.session.commit()
    return redirect(url_for('gamers'))

# --- PURGE ALL ---
@app.route('/purge', methods=['POST'])
def purge():
    db.session.query(Gamer).delete()
    db.session.commit()
    return redirect(url_for('gamers'))

# --- ENTRY POINT ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
