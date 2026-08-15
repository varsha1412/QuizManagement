from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "quiz_management_secret"


# Database connection
def get_db():
    conn = sqlite3.connect("quiz.db")
    conn.row_factory = sqlite3.Row
    return conn


# Create database tables
def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Home / Register
@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:
            return "Please fill all fields"

        conn = get_db()

        try:
            conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )

            conn.commit()

        except sqlite3.IntegrityError:
            conn.close()
            return "Email already registered"

        conn.close()

        return redirect("/login")

    return render_template("register.html")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE email = ? AND password = ?",
            (email, password)
        ).fetchone()

        conn.close()

        if user:
            session["email"] = email
            session["name"] = user["name"]

            return redirect("/dashboard")

        return "Invalid Email or Password"

    return render_template("login.html")


# Dashboard
@app.route("/dashboard")
def dashboard():

    if "email" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        name=session["name"]
    )


# Quiz
@app.route("/quiz", methods=["GET", "POST"])
def quiz():

    if "email" not in session:
        return redirect("/login")

    if request.method == "POST":

        score = 0

        if request.form.get("q1") == "A":
            score += 1

        if request.form.get("q2") == "B":
            score += 1

        if request.form.get("q3") == "C":
            score += 1

        if request.form.get("q4") == "A":
            score += 1

        if request.form.get("q5") == "B":
            score += 1

        total = 5

        conn = get_db()

        conn.execute(
            "INSERT INTO results (email, score, total) VALUES (?, ?, ?)",
            (session["email"], score, total)
        )

        conn.commit()
        conn.close()

        return render_template(
            "result.html",
            score=score,
            total=total
        )

    return render_template("quiz.html")


# Results
@app.route("/results")
def results():

    if "email" not in session:
        return redirect("/login")

    email = session["email"]

    conn = get_db()

    result = conn.execute(
        "SELECT score, total FROM results WHERE email = ? ORDER BY id DESC LIMIT 1",
        (email,)
    ).fetchone()

    conn.close()

    if result:
        return render_template(
            "result.html",
            score=result["score"],
            total=result["total"]
        )

    return "No quiz result found"


# Logout
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# Start application
if __name__ == "__main__":
    init_db()
    app.run(debug=True)