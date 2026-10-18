import os
import sqlite3
from pathlib import Path
from flask import Flask, request, redirect, url_for, session, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "dayflow-secret-key-rahasia"

# Path database (otomatis pakai /tmp jika di Vercel, atau lokal jika di laptop)
if os.environ.get("VERCEL"):
    DB = Path("/tmp/daily_planner.db")
else:
    DB = Path(__file__).resolve().parent.parent / "daily_planner.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    # Tabel User
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    # Tabel Tugas (terhubung dengan user_id)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            priority TEXT DEFAULT 'Medium',
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- TEMPLATE HTML INLINE ---
BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>{{ title }} - Dayflow</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background: #f4f3fb; color: #333; margin: 0; padding: 20px; display: flex; justify-content: center; }
        .card { background: white; border-radius: 12px; padding: 28px; width: 100%; max-width: 580px; box-shadow: 0 4px 15px rgba(0,0,0,0.06); }
        h1, h2 { color: #6b52ae; margin-top: 0; }
        input, select, button { width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
        button { background: #7867e8; color: white; border: none; font-weight: bold; cursor: pointer; transition: 0.2s; }
        button:hover { background: #6250d4; }
        .task-item { display: flex; align-items: center; justify-content: space-between; padding: 10px; border-bottom: 1px solid #eee; }
        .task-item.completed span { text-decoration: line-through; color: #888; }
        .badge { font-size: 11px; padding: 3px 8px; border-radius: 12px; background: #eee; margin-left: 8px; }
        .badge.High { background: #ffe4e6; color: #e11d48; }
        .nav-link { color: #7867e8; text-decoration: none; font-size: 13px; }
        .nav-link:hover { text-decoration: underline; }
        .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #f0f0f0; padding-bottom: 10px; }
    </style>
</head>
<body>
    <div class="card">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

# --- ROUTES AUTENTIKASI ---

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        hashed = generate_password_hash(password)
        
        try:
            conn = get_db()
            conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            return "Username sudah terdaftar! <a href='/register'>Coba lagi</a>"
            
    html = BASE_LAYOUT.replace("{% block content %}{% endblock %}", """
        <h2>Daftar Akun Dayflow 🌷</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Username / NIM" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Daftar</button>
        </form>
        <p style="font-size: 13px;">Sudah punya akun? <a class="nav-link" href="/login">Masuk di sini</a></p>
    """)
    return render_template_string(html, title="Register")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        return "Username atau password salah! <a href='/login'>Ulangi</a>"
        
    html = BASE_LAYOUT.replace("{% block content %}{% endblock %}", """
        <h2>Masuk ke Dayflow ✨</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Username / NIM" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Masuk</button>
        </form>
        <p style="font-size: 13px;">Belum punya akun? <a class="nav-link" href="/register">Buat akun baru</a></p>
    """)
    return render_template_string(html, title="Login")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# --- ROUTES TUGAS (TERISOLASI PER USER) ---

@app.route("/")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    conn = get_db()
    tasks = conn.execute(
        "SELECT * FROM tasks WHERE user_id = ? ORDER BY id DESC", 
        (session["user_id"],)
    ).fetchall()
    conn.close()
    
    html = BASE_LAYOUT.replace("{% block content %}{% endblock %}", """
        <div class="top-bar">
            <span>Halo, <b>{{ username }}</b> 👋</span>
            <a class="nav-link" href="/logout">Keluar (Logout)</a>
        </div>
        
        <h3>Tambah Jadwal Baru</h3>
        <form method="POST" action="/add" style="margin-bottom: 24px;">
            <input type="text" name="title" placeholder="Nama tugas / kegiatan..." required>
            <div style="display: flex; gap: 8px;">
                <input type="date" name="date" required>
                <select name="priority">
                    <option value="Low">Low</option>
                    <option value="Medium" selected>Medium</option>
                    <option value="High">High</option>
                </select>
            </div>
            <button type="submit">＋ Tambahkan ke Jadwal</button>
        </form>
        
        <h3>Daftar Tugasmu</h3>
        {% if not tasks %}
            <p style="color: #999; font-size: 14px;">Belum ada tugas tersimpan.</p>
        {% endif %}
        {% for t in tasks %}
            <div class="task-item {{ t['status'] }}">
                <div>
                    <span>{{ t['title'] }}</span>
                    <span class="badge {{ t['priority'] }}">{{ t['priority'] }}</span>
                    <span style="font-size: 11px; color: #888; margin-left: 6px;">📅 {{ t['date'] }}</span>
                </div>
                <div style="display: flex; gap: 8px;">
                    <a class="nav-link" href="/toggle/{{ t['id'] }}">[✓]</a>
                    <a class="nav-link" style="color: #e11d48;" href="/delete/{{ t['id'] }}">[✕]</a>
                </div>
            </div>
        {% endfor %}
    """)
    return render_template_string(html, title="Dashboard", username=session["username"], tasks=tasks)

@app.route("/add", methods=["POST"])
def add_task():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    title = request.form["title"].strip()
    date_val = request.form["date"]
    priority = request.form.get("priority", "Medium")
    
    conn = get_db()
    conn.execute(
        "INSERT INTO tasks (user_id, title, date, priority) VALUES (?, ?, ?, ?)",
        (session["user_id"], title, date_val, priority)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))

@app.route("/toggle/<int:task_id>")
def toggle_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    conn = get_db()
    task = conn.execute("SELECT status FROM tasks WHERE id = ? AND user_id = ?", (task_id, session["user_id"])).fetchone()
    if task:
        new_status = "pending" if task["status"] == "completed" else "completed"
        conn.execute("UPDATE tasks SET status = ? WHERE id = ? AND user_id = ?", (new_status, task_id, session["user_id"]))
        conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))

@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True)