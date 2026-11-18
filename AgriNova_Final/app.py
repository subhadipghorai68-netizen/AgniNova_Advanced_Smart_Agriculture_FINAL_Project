from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3, os, secrets
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "agrinova.db")
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("AGRINOVA_SECRET_KEY", secrets.token_hex(32))
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS users(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
          email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
          role TEXT NOT NULL DEFAULT 'farmer', created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS crops(
          id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
          name TEXT NOT NULL, variety TEXT DEFAULT '', area REAL DEFAULT 0,
          planted_on TEXT DEFAULT '', notes TEXT DEFAULT '',
          FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS soil_logs(
          id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
          field_name TEXT NOT NULL, ph REAL, moisture REAL, nitrogen REAL,
          phosphorus REAL, potassium REAL, logged_at TEXT NOT NULL,
          FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS tasks(
          id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
          title TEXT NOT NULL, due_date TEXT DEFAULT '', status TEXT DEFAULT 'Pending',
          FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """)
        admin = con.execute("SELECT id FROM users WHERE email=?", ("admin@agrinova.local",)).fetchone()
        if not admin:
            con.execute("INSERT INTO users(name,email,password_hash,role,created_at) VALUES(?,?,?,?,?)",
                ("AgriNova Admin","admin@agrinova.local",generate_password_hash("AgriNova@123"),"admin",datetime.now().isoformat(timespec="seconds")))
        con.commit()

def login_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please sign in to access your farm dashboard.", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapped

def current_user():
    if not session.get("user_id"): return None
    with db() as con:
        return con.execute("SELECT id,name,email,role FROM users WHERE id=?", (session["user_id"],)).fetchone()

@app.context_processor
def inject_globals():
    return {"current_user": current_user(), "year": datetime.now().year}

@app.route("/")
def index():
    if session.get("user_id"): return redirect(url_for("dashboard"))
    return render_template("landing.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        if len(name) < 2 or "@" not in email or len(password) < 8:
            flash("Enter a name, valid email and password of at least 8 characters.", "danger")
            return render_template("auth.html", mode="register")
        try:
            with db() as con:
                con.execute("INSERT INTO users(name,email,password_hash,role,created_at) VALUES(?,?,?,?,?)",
                    (name,email,generate_password_hash(password),"farmer",datetime.now().isoformat(timespec="seconds")))
                con.commit()
            flash("Account created. Please sign in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("This email already has an account. Please sign in.", "warning")
    return render_template("auth.html", mode="register")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email=request.form.get("email","").strip().lower()
        password=request.form.get("password","")
        with db() as con:
            user=con.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"]=user["id"]
            session["role"]=user["role"]
            session["name"]=user["name"]
            return redirect(url_for("dashboard"))
        flash("Email or password is incorrect.", "danger")
    return render_template("auth.html", mode="login")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have signed out.", "success")
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    uid=session["user_id"]
    with db() as con:
        crops=con.execute("SELECT * FROM crops WHERE user_id=? ORDER BY id DESC",(uid,)).fetchall()
        soils=con.execute("SELECT * FROM soil_logs WHERE user_id=? ORDER BY id DESC LIMIT 5",(uid,)).fetchall()
        tasks=con.execute("SELECT * FROM tasks WHERE user_id=? ORDER BY due_date ASC,id DESC",(uid,)).fetchall()
    return render_template("dashboard.html", crops=crops, soils=soils, tasks=tasks)

@app.route("/crops", methods=["GET","POST"])
@login_required
def crops_page():
    if request.method=="POST":
        with db() as con:
            con.execute("INSERT INTO crops(user_id,name,variety,area,planted_on,notes) VALUES(?,?,?,?,?,?)",
                (session["user_id"],request.form.get("name","").strip(),request.form.get("variety","").strip(),
                 float(request.form.get("area") or 0),request.form.get("planted_on",""),request.form.get("notes","").strip()))
            con.commit()
        flash("Crop record saved.", "success")
        return redirect(url_for("crops_page"))
    with db() as con:
        rows=con.execute("SELECT * FROM crops WHERE user_id=? ORDER BY id DESC",(session["user_id"],)).fetchall()
    return render_template("records.html", page="crops", rows=rows)

@app.route("/crops/delete/<int:item_id>", methods=["POST"])
@login_required
def delete_crop(item_id):
    with db() as con:
        con.execute("DELETE FROM crops WHERE id=? AND user_id=?",(item_id,session["user_id"]))
        con.commit()
    flash("Crop record deleted.", "success")
    return redirect(url_for("crops_page"))

@app.route("/soil", methods=["GET","POST"])
@login_required
def soil_page():
    if request.method=="POST":
        try:
            vals=[float(request.form.get(k) or 0) for k in ("ph","moisture","nitrogen","phosphorus","potassium")]
        except ValueError:
            flash("Please enter valid numeric soil values.", "danger")
            return redirect(url_for("soil_page"))
        with db() as con:
            con.execute("INSERT INTO soil_logs(user_id,field_name,ph,moisture,nitrogen,phosphorus,potassium,logged_at) VALUES(?,?,?,?,?,?,?,?)",
                (session["user_id"],request.form.get("field_name","My field").strip(),*vals,datetime.now().isoformat(timespec="seconds")))
            con.commit()
        flash("Soil test entry saved.", "success")
        return redirect(url_for("soil_page"))
    with db() as con:
        rows=con.execute("SELECT * FROM soil_logs WHERE user_id=? ORDER BY id DESC",(session["user_id"],)).fetchall()
    return render_template("records.html", page="soil", rows=rows)

@app.route("/tasks", methods=["GET","POST"])
@login_required
def tasks_page():
    if request.method=="POST":
        with db() as con:
            con.execute("INSERT INTO tasks(user_id,title,due_date) VALUES(?,?,?)",
                (session["user_id"],request.form.get("title","").strip(),request.form.get("due_date","")))
            con.commit()
        flash("Farm task added.", "success")
        return redirect(url_for("tasks_page"))
    with db() as con:
        rows=con.execute("SELECT * FROM tasks WHERE user_id=? ORDER BY due_date ASC,id DESC",(session["user_id"],)).fetchall()
    return render_template("records.html", page="tasks", rows=rows)

@app.route("/tasks/toggle/<int:item_id>", methods=["POST"])
@login_required
def toggle_task(item_id):
    with db() as con:
        row=con.execute("SELECT status FROM tasks WHERE id=? AND user_id=?",(item_id,session["user_id"])).fetchone()
        if row:
            status="Done" if row["status"]!="Done" else "Pending"
            con.execute("UPDATE tasks SET status=? WHERE id=? AND user_id=?",(status,item_id,session["user_id"]))
            con.commit()
    return redirect(url_for("tasks_page"))

@app.route("/tools")
@login_required
def tools_page():
    return render_template("tools.html")

@app.route("/technology")
@login_required
def technology():
    return render_template("technology.html")

@app.route("/api/summary")
@login_required
def api_summary():
    uid=session["user_id"]
    with db() as con:
        crops=con.execute("SELECT COUNT(*) n, COALESCE(SUM(area),0) area FROM crops WHERE user_id=?",(uid,)).fetchone()
        tasks=con.execute("SELECT COUNT(*) n FROM tasks WHERE user_id=? AND status!='Done'",(uid,)).fetchone()
        soil=con.execute("SELECT * FROM soil_logs WHERE user_id=? ORDER BY id DESC LIMIT 1",(uid,)).fetchone()
    return jsonify({"crop_count":crops["n"],"area":round(crops["area"],2),"pending_tasks":tasks["n"],"latest_soil":dict(soil) if soil else None})

@app.errorhandler(404)
def not_found(_): return render_template("error.html", code=404, message="That page could not be found."),404

if __name__=="__main__":
    init_db()
    app.run(host="127.0.0.1",port=5000,debug=False)
