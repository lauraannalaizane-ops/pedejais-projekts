from flask import Flask, render_template
import sqlite3
from pathlib import Path
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/kopejais")
def total():
    conn = get_db_connection()
    Gender = conn.execute("SELECT * FROM Gender LIMIT 2").fetchall()
    conn.close()
    return render_template("total.html", Gender=Gender)

@app.route("/kopejais/<int:gender_id>")
def products_show(gender_id, country_id):
    conn = get_db_connection() 
    Gender = conn.execute(
        "SELECT * FROM Total Score WHERE gender_id = ?",
        (gender_id,),
    ).fetchone()
    Country = conn.execute(
        "SELECT flag FROM Country Where country_id = ?",
        (country_id,),
    )
    conn.close()
    return render_template("total_show.html", Gender=Gender, Country=Country)

@app.route("/stafete")
def relay():
    conn = get_db_connection()
    Gender = conn.execute("SELECT * FROM Gender").fetchall()
    conn.close()
    return render_template("relay.html", Gender=Gender)

@app.route("/valstu")
def nation():
    conn = get_db_connection()
    Gender = conn.execute("SELECT * FROM Gender LIMIT 2").fetchall()
    conn.close()
    return render_template("nation.html", Gender=Gender)

def get_db_connection():
    db = Path(__file__).parent / "data.db"
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == "__main__":
    app.run(debug=True)