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
def total_show(gender_id):
    conn = get_db_connection()
    Total_score = conn.execute(
        """
        SELECT Total_score.*, Country.Flag AS flag, Gender.Gender AS gender
        FROM Total_score
        LEFT JOIN Country ON Total_score.Country_id = Country.id 
        LEFT JOIN Gender ON Total_score.Gender_id = Gender.id
        WHERE Total_score.Gender_id = ?
        """,
        (gender_id,),
    ).fetchall()
    conn.close()
    return render_template("total_show.html", Total_score=Total_score)


@app.route("/stafete")
def relay():
    conn = get_db_connection()
    Gender = conn.execute("SELECT * FROM Gender").fetchall()
    conn.close()
    return render_template("relay.html", Gender=Gender)

@app.route("/stafete/<int:gender_id>")
def relay_show(gender_id):
    conn = get_db_connection()
    Relay = conn.execute(
        """
        SELECT Nations.*, Country.Flag AS flag, Country.Country as country, Gender.Gender AS gender
        FROM Nations
        LEFT JOIN Country ON Nations.Country_id = Country.id
        LEFT JOIN Gender ON Nations.Gender_id = Gender.id
        WHERE Nations.Gender_id = ? AND Nations.Discipline_id = 2
        """,
        (gender_id,),
    ).fetchall()
    conn.close()
    return render_template("relay_show.html", Relay=Relay)

@app.route("/valstu")
def nation():
    conn = get_db_connection()
    Gender = conn.execute("SELECT * FROM Gender LIMIT 2").fetchall()
    conn.close()
    return render_template("nation.html", Gender=Gender)

@app.route("/valstu/<int:gender_id>")
def nation_show(gender_id):
    conn = get_db_connection()
    Cup = conn.execute(
        """
        SELECT Nations.*, Country.Flag AS flag, Country.Country as country, Gender.Gender AS gender
        FROM Nations
        LEFT JOIN Country ON Nations.Country_id = Country.id
        LEFT JOIN Gender ON Nations.Gender_id = Gender.id
        WHERE Nations.Gender_id = ? AND Nations.Discipline_id = 3
        """,
        (gender_id,),
    ).fetchall()
    conn.close()
    return render_template("nation_show.html", Cup=Cup)


def get_db_connection():
    db = Path(__file__).parent / "data.db"
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn


if __name__ == "__main__":
    app.run(debug=True)
