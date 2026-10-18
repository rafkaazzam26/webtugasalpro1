import os
import sqlite3
from pathlib import Path
from datetime import date, datetime
import calendar
from flask import Flask, request, redirect, url_for, session, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "dayflow-super-secret-key-undip"

# Path database: otomatis ke /tmp jika di Vercel agar tidak error read-only
if os.environ.get("VERCEL"):
    DB = Path("/tmp/daily_planner.db")
else:
    DB = Path(__file__).resolve().parent.parent / "daily_planner.db"

CATEGORIES = ["Personal", "Work", "Study", "Health", "Family", "Hobby"]
PRIORITIES = ["High", "Medium", "Low"]

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    # Tabel Pengguna (Multi-User)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    # Tabel Tugas (Terkait dengan user_id)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT DEFAULT '',
            category TEXT DEFAULT 'Personal',
            priority TEXT DEFAULT 'Medium',
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- TEMPLATE CSS ASLI DAYFLOW ---
CSS_STYLE = """
<style>
    :root {
        --primary: #7867e8;
        --primary-light: #ece9fb;
        --primary-dark: #5e4ec4;
        --bg: #f8f7fd;
        --surface: #ffffff;
        --text: #2d3142;
        --text-muted: #8c8fa7;
        --border: #edf0f7;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif; }
    body { background-color: var(--bg); color: var(--text); display: flex; min-height: 100vh; }
    aside { width: 260px; background: var(--surface); border-right: 1px solid var(--border); padding: 24px 20px; display: flex; flex-direction: column; gap: 24px; position: fixed; height: 100vh; }
    .brand { text-decoration: none; color: var(--primary); font-weight: 800; font-size: 20px; display: flex; flex-direction: column; }
    .brand small { font-size: 11px; color: var(--text-muted); font-weight: 400; margin-top: 2px; }
    .nav-group-title { font-size: 10px; font-weight: 700; color: var(--text-muted); letter-spacing: 0.8px; margin-bottom: 8px; }
    .nav-links { display: flex; flex-direction: column; gap: 4px; }
    .nav-links a { text-decoration: none; color: var(--text); padding: 9px 12px; border-radius: 8px; font-size: 13px; font-weight: 500; display: flex; align-items: center; gap: 10px; transition: 0.15s; }
    .nav-links a:hover, .nav-links a.active { background: var(--primary-light); color: var(--primary); }
    .quote-box { background: var(--primary-light); padding: 14px; border-radius: 10px; font-size: 12px; line-height: 1.5; color: var(--primary-dark); }
    .user-box { margin-top: auto; padding-top: 14px; border-top: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; font-size: 13px; }
    .logout-btn { color: #e11d48; text-decoration: none; font-size: 12px; font-weight: 600; }
    
    main { margin-left: 260px; flex: 1; padding: 32px 40px; max-width: 1000px; }
    .header-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
    .header-bar h1 { font-size: 24px; font-weight: 700; }
    .header-sub { font-size: 13px; color: var(--text-muted); }
    .date-badge { background: var(--surface); padding: 8px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; border: 1px solid var(--border); }

    .banner { background: linear-gradient(135deg, #7867e8, #9787ff); color: white; border-radius: 16px; padding: 24px 28px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; box-shadow: 0 8px 20px rgba(120, 103, 232, 0.2); }
    .banner h2 { font-size: 20px; margin-bottom: 6px; }
    .banner p { font-size: 13px; opacity: 0.9; line-height: 1.4; }
    .btn-add { background: white; color: var(--primary); padding: 10px 18px; border-radius: 10px; text-decoration: none; font-weight: 700; font-size: 13px; display: inline-block; margin-top: 14px; box-shadow: 0 4px 10px rgba(0,0,0,0.06); }
    
    .stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
    .stat-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 16px; text-align: center; }
    .stat-card strong { display: block; font-size: 26px; color: var(--primary); margin: 4px 0; }
    .stat-card .label { font-size: 12px; color: var(--text-muted); }
    .stat-card .sub { font-size: 11px; color: var(--text-muted); }

    .content-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
    .section-card { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 20px; margin-bottom: 20px; }
    .section-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
    .section-head h3 { font-size: 15px; font-weight: 700; }
    
    .task-row { display: flex; justify-content: space-between; align-items: center; padding: 12px; border-radius: 8px; border: 1px solid var(--border); margin-bottom: 8px; }
    .task-row.completed { opacity: 0.6; text-decoration: line-through; background: #fafafa; }
    .badge { font-size: 10px; padding: 3px 8px; border-radius: 12px; font-weight: 700; }
    .badge.High { background: #ffe4e6; color: #e11d48; }
    .badge.Medium { background: #fef3c7; color: #d97706; }
    .badge.Low { background: #e0f2fe; color: #0284c7; }

    .progress-bar { background: #edf0f7; height: 8px; border-radius: 10px; overflow: hidden; margin: 12px 0; }
    .progress-fill { background: var(--primary); height: 100%; border-radius: 10px; transition: width 0.3s ease; }
    
    /* Form Modal / Single View */
    .form-group { margin-bottom: 12px; }
    .form-group label { display: block; font-size: 12px; font-weight: 600; margin-bottom: 4px; }
    .form-group input, .form-group select { width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 8px; font-size: 13px; }
    .btn-submit { background: var(--primary); color: white; border: none; padding: 10px 16px; border-radius: 8px; font-weight: 700; cursor: pointer; width: 100%; }

    footer { text-align: center; margin-top: 30px; font-size: 12px; color: var(--text-muted); }
</style>
"""

# --- HALAMAN AUTENTIKASI (LOGIN & REGISTER) ---
AUTH_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>{{ title }} - Dayflow</title>
    {{ css|safe }}
</head>
<body style="align-items: center; justify-content: center;">
    <div style="background: white; border: 1px solid var(--border); border-radius: 16px; padding: 32px; width: 100%; max-width: 360px; box-shadow: 0 10px 25px rgba(0,0,0,0.05);">
        <div style="text-align: center; margin-bottom: 24px;">
            <div style="font-size: 26px; font-weight: 800; color: var(--primary);">✳ dayflow.</div>
            <div style="font-size: 12px; color: var(--text-muted);">Your space to focus</div>
        </div>
        <h2 style="font-size: 18px; margin-bottom: 16px; text-align: center;">{{ heading }}</h2>
        {% if error %}
            <div style="background: #ffe4e6; color: #e11d48; font-size: 12px; padding: 8px 12px; border-radius: 6px; margin-bottom: 12px; text-align: center;">{{ error }}</div>
        {% endif %}
        <form method="POST">
            <div class="form-group">
                <label>Username / NIM</label>
                <input type="text" name="username" placeholder="Masukkan username" required>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" placeholder="Masukkan password" required>
            </div>
            <button class="btn-submit" type="submit" style="margin-top: 8px;">{{ btn_text }}</button>
        </form>
        <div style="text-align: center; margin-top: 18px; font-size: 12px;">
            {% if title == 'Login' %}
                Belum punya akun? <a href="/register" style="color: var(--primary); font-weight: 600; text-decoration: none;">Daftar di sini</a>
            {% else %}
                Sudah punya akun? <a href="/login" style="color: var(--primary); font-weight: 600; text-decoration: none;">Masuk di sini</a>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

# --- ROUTES AUTENTIKASI ---
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username and password:
            try:
                conn = get_db()
                conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                             (username, generate_password_hash(password)))
                conn.commit()
                conn.close()
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                error = "Username sudah dipakai, coba username lain!"
    return render_template_string(AUTH_TEMPLATE, title="Daftar", heading="Buat Akun Dayflow 🌷", btn_text="Daftar Sekarang", error=error, css=CSS_STYLE)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("index"))
        error = "Username atau password keliru."
    return render_template_string(AUTH_TEMPLATE, title="Login", heading="Selamat Datang ✨", btn_text="Masuk ke Akun", error=error, css=CSS_STYLE)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# --- ROUTE DASHBOARD ASLI (TERHUBUNG KE USER AKTIF) ---
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    today_str = date.today().isoformat()
    selected_date = request.args.get("date", today_str)

    conn = get_db()
    # Hanya ambil tugas milik user yang sedang login
    tasks = conn.execute("SELECT * FROM tasks WHERE user_id = ? AND date = ? ORDER BY id DESC", (user_id, selected_date)).fetchall()
    all_user_tasks = conn.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,)).fetchall()
    high_priority_tasks = conn.execute("SELECT * FROM tasks WHERE user_id = ? AND priority = 'High' AND status != 'completed'", (user_id,)).fetchall()
    conn.close()

    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t["status"] == "completed")
    pending_tasks = total_tasks - completed_tasks
    progress_pct = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0

    hari_map = {0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 4: "Jumat", 5: "Sabtu", 6: "Minggu"}
    bulan_map = {1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"}
    now = datetime.now()
    formatted_date = f"{hari_map[now.weekday()]}, {now.day} {bulan_map[now.month]} {now.year}"

    html = f"""
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <title>Dayflow · Your space to focus</title>
        {CSS_STYLE}
    </head>
    <body>
        <aside>
            <a href="/" class="brand">
                ✳ dayflow.
                <small>Your space to focus</small>
            </a>
            <div>
                <div class="nav-group-title">WORKSPACE</div>
                <div class="nav-links">
                    <a href="/" class="active">▦ Dashboard</a>
                    <a href="/tasks">☷ My Tasks</a>
                    <a href="/?date={today_str}">☀ Today</a>
                    <a href="/calendar">▦ Calendar</a>
                    <a href="/tasks?status=completed">✓ Completed</a>
                </div>
            </div>
            <div class="quote-box">
                ✦ Mulai dari satu hal kecil. Atur jadwalmu dan jalani hari dengan tenang.
            </div>
            <div class="user-box">
                <span>👤 <b>{session.get('username')}</b></span>
                <a href="/logout" class="logout-btn">Keluar</a>
            </div>
        </aside>

        <main>
            <div class="header-bar">
                <div>
                    <div class="header-sub">YOUR DAILY SPACE</div>
                    <h1>Selamat datang, {session.get('username')} ✨</h1>
                    <div class="header-sub">Rencanakan harimu, fokus pada yang penting.</div>
                </div>
                <div class="date-badge">📅 {formatted_date}</div>
            </div>

            <section class="banner">
                <div>
                    <h2>Make today count 🌷</h2>
                    <p>Langkah kecil setiap hari membawa perubahan besar.<br>Atur jadwalmu dengan tenang.</p>
                    <a href="/add" class="btn-add">＋ Tambah kegiatan</a>
                </div>
                <div style="font-size: 46px;">☁️</div>
            </section>

            <section class="stats-grid">
                <div class="stat-card">
                    <div class="label">Total tugas</div>
                    <strong>{total_tasks}</strong>
                    <div class="sub">Untuk tanggal ini</div>
                </div>
                <div class="stat-card">
                    <div class="label">Selesai ✓</div>
                    <strong style="color: #10b981;">{completed_tasks}</strong>
                    <div class="sub">Good job!</div>
                </div>
                <div class="stat-card">
                    <div class="label">Belum selesai ◷</div>
                    <strong style="color: #f59e0b;">{pending_tasks}</strong>
                    <div class="sub">Satu langkah lagi</div>
                </div>
            </section>

            <div class="content-grid">
                <div>
                    <div class="section-card">
                        <div class="section-head">
                            <div>
                                <h3>Today's schedule</h3>
                                <div class="header-sub">Jadwal kegiatanmu</div>
                            </div>
                            <a href="/tasks" style="color: var(--primary); font-size: 12px; font-weight: 700; text-decoration: none;">Semua →</a>
                        </div>
                        
                        <div>
                        """ + ("""
                            <div style="text-align: center; padding: 30px; color: var(--text-muted); font-size: 13px;">
                                🌤️<br><b>Belum ada jadwal.</b><br>Tambahkan kegiatan pertamamu hari ini.
                            </div>
                        """ if not tasks else "".join([f"""
                            <div class="task-row {'completed' if t['status'] == 'completed' else ''}">
                                <div>
                                    <span style="font-weight: 600; font-size: 14px;">{t['title']}</span>
                                    <span class="badge {t['priority']}">{t['priority']}</span>
                                    <span style="font-size: 11px; color: var(--text-muted); margin-left: 6px;">🏷️ {t['category']}</span>
                                </div>
                                <div style="display: flex; gap: 8px;">
                                    <a href="/toggle/{t['id']}" style="text-decoration: none;">{'↩️' if t['status'] == 'completed' else '✅'}</a>
                                    <a href="/delete/{t['id']}" style="text-decoration: none; color: #e11d48;">🗑️</a>
                                </div>
                            </div>
                        """ for t in tasks])) + f"""
                        </div>
                    </div>
                </div>

                <div>
                    <div class="section-card">
                        <div class="section-head">
                            <h3>Daily progress</h3> 🌱
                        </div>
                        <div style="font-size: 26px; font-weight: 800; color: var(--primary);">{progress_pct}%</div>
                        <div class="header-sub">Terus bergerak sesuai kemampuanmu.</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {progress_pct}%;"></div>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 11px; color: var(--text-muted);">
                            <span>{completed_tasks} selesai</span>
                            <span>{total_tasks} tugas</span>
                        </div>
                    </div>

                    <div class="section-card">
                        <div class="section-head">
                            <h3>Prioritas tinggi</h3> 🔥
                        </div>
                        """ + ("""
                            <div style="color: var(--text-muted); font-size: 12px; text-align: center; padding: 12px;">Tidak ada prioritas tinggi 🌼</div>
                        """ if not high_priority_tasks else "".join([f"""
                            <div style="font-size: 13px; font-weight: 600; padding: 6px 0; border-bottom: 1px solid var(--border);">
                                • {t['title']} <span style="font-size: 10px; color: var(--text-muted);">({t['date']})</span>
                            </div>
                        """ for t in high_priority_tasks])) + f"""
                    </div>
                </div>
            </div>

            <footer>Dayflow · Plan gently, grow daily ✨</footer>
        </main>
    </body>
    </html>
    """
    return html

# --- ROUTE TAMBAH KEGIATAN ---
@app.route("/add", methods=["GET", "POST"])
def add():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        task_date = request.form.get("date", date.today().isoformat())
        category = request.form.get("category", "Personal")
        priority = request.form.get("priority", "Medium")

        if title:
            conn = get_db()
            conn.execute(
                "INSERT INTO tasks (user_id, title, date, category, priority) VALUES (?, ?, ?, ?, ?)",
                (session["user_id"], title, task_date, category, priority)
            )
            conn.commit()
            conn.close()
        return redirect(url_for("index"))

    return f"""
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <title>Tambah Kegiatan - Dayflow</title>
        {CSS_STYLE}
    </head>
    <body style="align-items: center; justify-content: center;">
        <div style="background: white; border: 1px solid var(--border); border-radius: 16px; padding: 28px; width: 100%; max-width: 440px;">
            <h2 style="font-size: 18px; margin-bottom: 16px;">＋ Tambah Kegiatan Baru</h2>
            <form method="POST">
                <div class="form-group">
                    <label>Nama Kegiatan</label>
                    <input type="text" name="title" placeholder="Contoh: Belajar Python Alpro" required>
                </div>
                <div class="form-group">
                    <label>Tanggal</label>
                    <input type="date" name="date" value="{date.today().isoformat()}" required>
                </div>
                <div class="form-group">
                    <label>Kategori</label>
                    <select name="category">
                        {''.join([f'<option value="{c}">{c}</option>' for c in CATEGORIES])}
                    </select>
                </div>
                <div class="form-group">
                    <label>Prioritas</label>
                    <select name="priority">
                        {''.join([f'<option value="{p}">{p}</option>' for p in PRIORITIES])}
                    </select>
                </div>
                <button class="btn-submit" type="submit" style="margin-top: 10px;">Simpan Kegiatan</button>
                <div style="text-align: center; margin-top: 12px;">
                    <a href="/" style="font-size: 12px; color: var(--text-muted); text-decoration: none;">← Batal</a>
                </div>
            </form>
        </div>
    </body>
    </html>
    """

# --- ROUTE ACTIONS (TOGGLE & DELETE) ---
@app.route("/toggle/<int:task_id>")
def toggle(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    task = conn.execute("SELECT status FROM tasks WHERE id = ? AND user_id = ?", (task_id, session["user_id"])).fetchone()
    if task:
        new_status = "pending" if task["status"] == "completed" else "completed"
        conn.execute("UPDATE tasks SET status = ? WHERE id = ? AND user_id = ?", (new_status, task_id, session["user_id"]))
        conn.commit()
    conn.close()
    return redirect(request.referrer or url_for("index"))

@app.route("/delete/<int:task_id>")
def delete(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, session["user_id"]))
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for("index"))

@app.route("/tasks")
def tasks_page():
    return redirect(url_for("index"))

@app.route("/calendar")
def calendar_page():
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)