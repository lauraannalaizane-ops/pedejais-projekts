from flask import Flask, render_template, session, request, redirect, url_for
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "dirssBalonā76"


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



@app.route("/log-in", methods=["GET", "POST"])
def log_in():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM Accounts WHERE email = ?", (email,)
        ).fetchone()

        conn.close()

        if user is None:
            return render_template("log-in.html", first=False)

        if not check_password_hash(user["password"], password):
            return render_template("log-in.html", first=False)

        session["user_id"] = user["id"]
        session["username"] = user["username"]

        return redirect(url_for("index"))

    return render_template("log-in.html", first=True)


@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        username = request.form.get("username")

        conn = get_db_connection()

        emails = conn.execute(
            "SELECT * FROM Accounts WHERE email = ?", (email,)
        ).fetchone()

        usernames = conn.execute(
            "SELECT * FROM Accounts WHERE username = ?", (username,)
        ).fetchone()

        if emails is not None:
            conn.close()
            return render_template(
                "sign_up.html", mistake="This e-mail already has an account registered"
            )

        elif usernames is not None:
            conn.close()
            return render_template("sign_up.html", mistake="Username taken")

        hashed_password = generate_password_hash(password)

        conn.execute(
            "INSERT INTO Accounts (email, password, username) VALUES (?, ?, ?)",
            (email, hashed_password, username),
        )
        conn.commit()
        

        user = conn.execute(
            "SELECT * FROM Accounts WHERE email = ?", (email,)
        ).fetchone()

        conn.close()

        session["user_id"] = user["id"]
        session["username"] = user["username"]

        return redirect(url_for("index"))

    return render_template("sign_up.html")



@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("log_in"))
    conn = get_db_connection()

    user = conn.execute(
        "SELECT * FROM Accounts WHERE id = ?", (session["user_id"],)
    ).fetchone()

    if request.method == "POST":
        username = request.form.get("username")
        new_password = request.form.get("new_password")
        new_password_2 = request.form.get("new_password_2")
        password = request.form.get("password")

        if len(username) == 0:
            new_username = user["username"]
        if len(new_password) == 0:
            new_hashed = user["password"]

        if len(username) != 0:
            if not check_password_hash(user["password"], password):
                return render_template(
                    "profile.html", mistake="Wrong password on confirm", user=user
                )
            else:
                new_username = username
        if len(new_password) != 0:
            if new_password != new_password_2:
                return render_template(
                    "profile.html",
                    edit_error="2nd password must match the first one",
                    user=user,
                )
            elif not check_password_hash(user["password"], password):
                return render_template(
                    "profile.html", edit_error="Wrong password on confirm", user=user
                )
            else:
                new_hashed = generate_password_hash(new_password)

        conn.execute(
            "UPDATE Accounts SET username = ?, password = ? WHERE id = ?",
            (new_username, new_hashed, session["user_id"]),
        )
        conn.commit()

        return redirect(url_for("index"))
    conn.close()
    return render_template("profile.html", user=user)



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))



@app.route("/delete-profile", methods=["POST"])
def delete_profile():
    password = request.form.get("password")

    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM Accounts WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    if not check_password_hash(user["password"], password):
        return render_template(
                    "profile.html", delete_error="Wrong password", user=user
                )


    conn.execute(
        "DELETE FROM Accounts WHERE id = ?",
        (session["user_id"],)
    )
    conn.commit()
    conn.close()

    session.clear()
    return redirect(url_for("index"))



if __name__ == "__main__":
    app.run(debug=True)
