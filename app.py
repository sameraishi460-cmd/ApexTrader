# from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "p2p_usdt_palestine"


def connect():
    db = sqlite3.connect("database.db")
    db.row_factory = sqlite3.Row
    return db


def init_db():
    db = connect()
    cur = db.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ads(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        type TEXT,
        amount REAL,
        price REAL,
        payment TEXT,
        status TEXT
    )
    """)

    db.commit()
    db.close()


@app.route("/")
def home():
    db = connect()
    ads = db.execute(
        "SELECT * FROM ads WHERE status='OPEN'"
    ).fetchall()
    db.close()

    return render_template("index.html", ads=ads)


@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(
            request.form["password"]
        )

        db = connect()

        try:
            db.execute(
                "INSERT INTO users(username,email,password) VALUES(?,?,?)",
                (username,email,password)
            )
            db.commit()

        except:
            return "الإيميل مستخدم"

        db.close()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        email=request.form["email"]
        password=request.form["password"]

        db=connect()

        user=db.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        ).fetchone()

        db.close()

        if user and check_password_hash(user["password"],password):

            session["user"]=user["username"]
            return redirect("/")

        return "خطأ في البيانات"

    return render_template("login.html")


@app.route("/create_ad", methods=["GET","POST"])
def create_ad():

    if "user" not in session:
        return redirect("/login")


    if request.method=="POST":

        ad_type=request.form["type"]
        amount=request.form["amount"]
        price=request.form["price"]
        payment=request.form["payment"]


        db=connect()

        db.execute("""
        INSERT INTO ads
        (user,type,amount,price,payment,status)
        VALUES(?,?,?,?,?,?)
        """,
        (
        session["user"],
        ad_type,
        amount,
        price,
        payment,
        "OPEN"
        ))

        db.commit()
        db.close()

        return redirect("/")


    return render_template("create_ad.html")



@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")



if __name__=="__main__":

    init_db()

    app.run(
        host="0.0.0.0",
        port=5000
    )
