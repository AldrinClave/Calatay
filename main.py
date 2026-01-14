from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import uuid
import os

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('gamer_system.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    # Create table with all columns
    conn.execute('''
        CREATE TABLE IF NOT EXISTS gamers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            favorite_game TEXT NOT NULL,
            platform TEXT,
            region TEXT,
            rank TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

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

    agent_id = f"MG-{str(uuid.uuid4())[:4].upper()}"
    identity = f"{agent_id} | {username}"

    conn = get_db()
    conn.execute("INSERT INTO gamers (username, favorite_game, rank, platform, region) VALUES (?, ?, ?, ?, ?)",
                 (identity, game, rank, platform, region))
    conn.commit()
    conn.close()
    return redirect(url_for('gamers'))

@app.route('/gamers')
def gamers():
    conn = get_db()
    rows = conn.execute("SELECT * FROM gamers ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('gamers.html', gamers=rows)

# --- NEW PURGE ROUTE ---
@app.route('/purge', methods=['POST'])
def purge():
    conn = get_db()
    conn.execute("DELETE FROM gamers")
    conn.execute("DELETE FROM sqlite_sequence WHERE name='gamers'") # Resets ID to 1
    conn.commit()
    conn.close()
    return redirect(url_for('gamers'))

# Add this for the individual PURGE buttons
@app.route('/delete/<int:id>')
def delete_gamer(id):
    conn = get_db()
    conn.execute("DELETE FROM gamers WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('gamers'))

# Add this if you want a "Purge All" button
@app.route('/purge_all', methods=['POST'])
def purge_all():
    conn = get_db()
    conn.execute("DELETE FROM gamers")
    conn.execute("DELETE FROM sqlite_sequence WHERE name='gamers'") # Resets IDs to 1
    conn.commit()
    conn.close()
    return redirect(url_for('gamers'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)