from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "palp2p_secret_key"


# الاتصال بقاعدة البيانات
def db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# إنشاء الجداول
def init_db():

    conn = db()
    cur = conn.cursor()

    # المستخدمين
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    # الإعلانات
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

    # الصفقات
    cur.execute("""
    CREATE TABLE IF NOT EXISTS trades(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        buyer TEXT,
        seller TEXT,
        amount REAL,
        price REAL,
        status TEXT,
        fee REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # العمولات
    cur.execute("""
    CREATE TABLE IF NOT EXISTS fees(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trade_id INTEGER,
        amount REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)


    conn.commit()
    conn.close()



# الصفحة الرئيسية
@app.route("/")
def home():

    conn = db()

    ads = conn.execute(
        "SELECT * FROM ads WHERE status='OPEN'"
    ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        ads=ads
    )



# تسجيل حساب
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]

        password = generate_password_hash(
            request.form["password"]
        )

        conn = db()

        try:

            conn.execute(
            """
            INSERT INTO users
            (username,email,password)
            VALUES(?,?,?)
            """,
            (username,email,password)
            )

            conn.commit()

        except:

            return "الإيميل مستخدم"

        conn.close()

        return redirect("/login")


    return render_template("register.html")




# تسجيل دخول
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method=="POST":

        email=request.form["email"]
        password=request.form["password"]

        conn=db()

        user=conn.execute(
        """
        SELECT * FROM users
        WHERE email=?
        """,
        (email,)
        ).fetchone()

        conn.close()


        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user"]=user["username"]

            return redirect("/")


        return "بيانات خاطئة"


    return render_template("login.html")





# إنشاء إعلان
@app.route("/create_ad", methods=["GET","POST"])
def create_ad():

    if "user" not in session:
        return redirect("/login")


    if request.method=="POST":

        conn=db()

        conn.execute(
        """
        INSERT INTO ads
        (user,type,amount,price,payment,status)
        VALUES(?,?,?,?,?,?)
        """,
        (
        session["user"],
        request.form["type"],
        request.form["amount"],
        request.form["price"],
        request.form["payment"],
        "OPEN"
        )
        )


        conn.commit()
        conn.close()

        return redirect("/")


    return render_template("create_ad.html")





# بدء صفقة شراء
@app.route("/buy/<int:ad_id>")
def buy(ad_id):

    if "user" not in session:
        return redirect("/login")


    conn=db()


    ad=conn.execute(
    """
    SELECT * FROM ads
    WHERE id=?
    """,
    (ad_id,)
    ).fetchone()


    if not ad:
        return "الإعلان غير موجود"



    fee = ad["amount"] * 0.02


    conn.execute(
    """
    INSERT INTO trades
    (buyer,seller,amount,price,status,fee)
    VALUES(?,?,?,?,?,?)
    """,
    (
    session["user"],
    ad["user"],
    ad["amount"],
    ad["price"],
    "USDT_LOCKED",
    fee
    )
    )


    conn.execute(
    """
    UPDATE ads
    SET status='CLOSED'
    WHERE id=?
    """,
    (ad_id,)
    )


    conn.commit()
    conn.close()


    return "تم فتح الصفقة وحجز USDT"





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
