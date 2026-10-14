
from flask import Flask, request, redirect, url_for, render_template_string, abort
import sqlite3
import socket
import threading
import webbrowser
from pathlib import Path
from datetime import date, datetime
import calendar

app = Flask(__name__)
DB = Path(__file__).with_name("daily_planner.db")

CATEGORIES = ["Personal", "Work", "Study", "Health", "Family", "Hobby"]
PRIORITIES = ["High", "Medium", "Low"]


# =========================================================
# DATABASE
# =========================================================

def connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                task_date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'Personal',
                priority TEXT NOT NULL DEFAULT 'Medium',
                notes TEXT DEFAULT '',
                done INTEGER NOT NULL DEFAULT 0
            )
        """)


init_db()


# =========================================================
# STYLE
# =========================================================

STYLE = """
*{box-sizing:border-box}
body{margin:0;background:#f7f7fc;color:#292940;font-family:Arial,sans-serif}
a{text-decoration:none;color:inherit}
button,input,select,textarea{font:inherit}
.layout{display:flex;min-height:100vh}
aside{width:220px;background:white;padding:24px 15px;border-right:1px solid #eaeaf3;flex-shrink:0}
.brand{font-size:23px;font-weight:bold;color:#7867e8;margin-bottom:35px;display:block}
.brand small{display:block;font-size:11px;color:#85869d;font-weight:normal;margin-top:5px}
.nav{display:block;padding:12px;border-radius:10px;margin:5px 0;font-size:13px;color:#77788f}
.nav:hover,.active{background:#f0edff;color:#7867e8}
.label{font-size:10px;color:#aaa;letter-spacing:1px;margin:25px 10px 10px}
main{flex:1;min-width:0;padding:28px clamp(14px,4vw,42px)}
.top{display:flex;justify-content:space-between;align-items:center;gap:12px}
.eyebrow{font-size:10px;letter-spacing:2px;color:#7867e8;font-weight:bold}
h1{font-size:clamp(25px,4vw,35px);margin:10px 0}
.muted{color:#85869d;font-size:12px;line-height:1.6}
.today{background:white;padding:11px;border:1px solid #eaeaf3;border-radius:10px;font-size:11px}
.hero{margin-top:25px;padding:26px;border-radius:19px;color:white;background:linear-gradient(115deg,#7867e8,#b3a5f8);display:flex;justify-content:space-between;align-items:center;gap:12px}
.hero h2{margin:0 0 10px;font-size:23px}
.hero p{font-size:13px;line-height:1.7;color:#f4f0ff}
.hero-icon{font-size:42px;animation:float 3s infinite ease-in-out}
@keyframes float{50%{transform:translateY(-8px)}}
.stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:20px 0}
.stat,.panel{background:white;border:1px solid #eaeaf3;border-radius:16px;box-shadow:0 6px 25px #30305208}
.stat{padding:16px}
.stat strong{display:block;font-size:28px;margin:12px 0}
.content{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(220px,.8fr);gap:16px;align-items:start}
.panel{padding:18px;min-width:0}
.head{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:16px}
h3{margin:0;font-size:16px}
.btn{display:inline-block;border:0;background:#7867e8;color:white;padding:10px 13px;border-radius:9px;font-size:12px;font-weight:bold;cursor:pointer}
.light{background:#f0edff;color:#7867e8}
.danger{background:#fff0f1;color:#c44b63}
input,select,textarea{width:100%;min-width:0;padding:11px;border:1px solid #e4e4ef;border-radius:9px;background:white;color:#292940}
textarea{min-height:85px;resize:vertical}
label{display:block;font-size:12px;font-weight:bold;margin-bottom:7px;color:#666980}
.field{margin-bottom:15px}
.formgrid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.full{grid-column:1/-1}
.filter{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}
.filter input{max-width:180px}
.tasklist{display:flex;flex-direction:column;gap:10px}
.task{display:flex;gap:10px;padding:13px;border:1px solid #eaeaf3;border-radius:12px;min-width:0}
.task:hover{border-color:#d4ccff}
.task.done{background:#fbfbfd}
.check{width:18px;height:18px;accent-color:#7867e8;margin-top:2px}
.taskbody{flex:1;min-width:0}
.tasktitle{font-size:13px;font-weight:bold;overflow-wrap:anywhere}
.done .tasktitle{text-decoration:line-through;color:#aaa}
.tags,.actions{display:flex;flex-wrap:wrap;gap:6px;margin-top:9px}
.tag{font-size:10px;padding:5px 8px;border-radius:6px;background:#f0f0f7;color:#73748a}
.purple{background:#f0edff;color:#7867e8}
.red{background:#ffe7eb;color:#c14f67}
.green{background:#e1f7e9;color:#338359}
.mini{font-size:10px;padding:6px 8px;border:1px solid #eaeaf3;border-radius:7px;background:white;color:#77798c;cursor:pointer}
.actions form{display:inline}
.empty{text-align:center;padding:25px 10px;color:#85869d;font-size:12px;line-height:1.8}
.progress{height:8px;background:#efedf9;border-radius:20px;overflow:hidden;margin:14px 0}
.bar{height:100%;background:linear-gradient(90deg,#7867e8,#b3a4f8)}
.row{display:flex;justify-content:space-between;color:#85869d;font-size:11px}
.priority{padding:12px 0;border-bottom:1px solid #eaeaf3;font-size:12px;overflow-wrap:anywhere}
.priority small{display:block;color:#85869d;margin-top:5px}
.calendar{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:5px;margin:15px 0}
.weekday{text-align:center;font-size:10px;color:#85869d;padding:8px 0}
.day{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;min-height:40px;border-radius:8px;font-size:12px}
.day:hover,.selected{background:#7867e8;color:white}
.dot{width:4px;height:4px;border-radius:50%;background:#43b981}
.selected .dot{background:white}
footer{text-align:center;color:#aaaabd;font-size:11px;padding:28px 0}
.network{margin-top:20px;padding:14px;background:#f0edff;border-radius:12px;font-size:12px;line-height:1.8}
.network a{color:#7867e8;overflow-wrap:anywhere}
@media(max-width:850px){
    aside{width:180px}
    .content{grid-template-columns:1fr}
}
@media(max-width:600px){
    .layout{display:block}
    aside{width:100%;padding:12px;border-right:0;border-bottom:1px solid #eaeaf3}
    .brand{margin-bottom:10px}
    .brand small,.label{display:none}
    .navs{display:flex;gap:3px;overflow-x:auto}
    .nav{white-space:nowrap;padding:9px;font-size:11px}
    main{padding:20px 12px}
    .stats{gap:7px}
    .stat{padding:11px 9px}
    .stat strong{font-size:23px}
    .content{grid-template-columns:1fr}
    .hero{padding:20px 15px}
    .hero h2{font-size:19px}
    .hero-icon{font-size:32px}
    .panel{padding:14px}
    .formgrid{grid-template-columns:1fr}
    .full{grid-column:auto}
}
"""


# =========================================================
# HTML
# =========================================================

HTML = """
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ title }} | Dayflow</title>
<style>""" + STYLE + """</style>
</head>
<body>
<div class="layout">
<aside>
<a href="/" class="brand">
    ✳ dayflow.
    <small>Your space to focus</small>
</a>

<div class="label">WORKSPACE</div>
<div class="navs">
<a class="nav {{ 'active' if page=='home' else '' }}" href="/">▦ Dashboard</a>
<a class="nav {{ 'active' if page=='tasks' else '' }}" href="/tasks">☷ My Tasks</a>
<a class="nav" href="/?date={{ now }}">☀ Today</a>
<a class="nav {{ 'active' if page=='calendar' else '' }}" href="/calendar">▦ Calendar</a>
<a class="nav" href="/tasks?status=completed">✓ Completed</a>
</div>

<div class="label">YOUR SPACE</div>
<div class="muted" style="padding:10px">
✦ Mulai dari satu hal kecil. Atur jadwalmu dan jalani hari dengan tenang.
</div>

<div class="network">
<b>🌐 Akses jaringan lokal</b><br>
Buka dari HP yang terhubung ke Wi-Fi yang sama:<br>
<a href="{{ lan_url }}">{{ lan_url }}</a>
</div>
</aside>

<main>
<div class="top">
<div>
<div class="eyebrow">YOUR DAILY SPACE</div>
<h1>{{ greeting }} ✨</h1>
<div class="muted">Rencanakan harimu, fokus pada yang penting.</div>
</div>
<div class="today">📅 {{ today_label }}</div>
</div>

{% if page=='home' %}
<section class="hero">
<div>
<h2>Make today count 🌷</h2>
<p>Langkah kecil setiap hari membawa perubahan besar.<br>Atur jadwalmu dengan tenang.</p>
<a class="btn" style="background:white;color:#7867e8" href="/add">＋ Tambah kegiatan</a>
</div>
<div class="hero-icon">☁️</div>
</section>

<section class="stats">
<div class="stat">
<div class="muted">Total tugas</div>
<strong>{{ total }}</strong>
<div class="muted">Untuk tanggal ini</div>
</div>
<div class="stat">
<div class="muted">Selesai ✓</div>
<strong>{{ completed }}</strong>
<div class="muted">Good job!</div>
</div>
<div class="stat">
<div class="muted">Belum selesai ◷</div>
<strong>{{ remaining }}</strong>
<div class="muted">Satu langkah lagi</div>
</div>
</section>

<div class="content">
<section class="panel">
<div class="head">
<div>
<h3>Today's schedule</h3>
<div class="muted">Jadwal kegiatanmu</div>
</div>
<a class="btn light" href="/tasks">Semua →</a>
</div>

<form class="filter">
<input type="date" name="date" value="{{ selected_date }}">
<button class="btn">Lihat</button>
<a class="btn light" href="/">Hari ini</a>
</form>

<div class="tasklist">
{% for t in task_list %}
<article class="task {{ 'done' if t.done else '' }}">
<form method="post" action="/toggle/{{ t.id }}">
<input class="check" type="checkbox" {{ 'checked' if t.done else '' }} onchange="this.form.submit()">
</form>
<div class="taskbody">
<div class="tasktitle">{{ t.title }}</div>
<div class="tags">
<span class="tag purple">◷ {{ t.start_time }}–{{ t.end_time }}</span>
<span class="tag">{{ t.category }}</span>
<span class="tag {{ 'red' if t.priority=='High' else ('green' if t.priority=='Low' else '') }}">{{ t.priority }}</span>
</div>
{% if t.notes %}
<div class="muted" style="margin-top:8px">{{ t.notes }}</div>
{% endif %}
<div class="actions">
<a class="mini" href="/edit/{{ t.id }}">✎ Edit</a>
<form method="post" action="/delete/{{ t.id }}" onsubmit="return confirm('Hapus kegiatan ini?')">
<button class="mini">⌫ Hapus</button>
</form>
</div>
</div>
</article>
{% else %}
<div class="empty">🌤️<br><b>Belum ada jadwal.</b><br>Tambahkan kegiatan pertamamu hari ini.</div>
{% endfor %}
</div>
</section>

<div style="display:flex;flex-direction:column;gap:16px">
<section class="panel">
<div class="head"><h3>Daily progress</h3>🌱</div>
<div style="font-size:28px;font-weight:bold">{{ progress }}%</div>
<div class="muted">Terus bergerak sesuai kemampuanmu.</div>
<div class="progress"><div class="bar" style="width:{{ progress }}%"></div></div>
<div class="row"><span>{{ completed }} selesai</span><span>{{ total }} tugas</span></div>
</section>

<section class="panel">
<div class="head"><h3>Prioritas tinggi</h3>🔥</div>
{% for t in high_priority %}
<div class="priority">
<b>{{ t.title }}</b>
<small>{{ t.start_time }} · {{ t.category }}</small>
</div>
{% else %}
<div class="empty">Tidak ada prioritas tinggi 🌼</div>
{% endfor %}
</section>
</div>
</div>

{% elif page=='tasks' %}
<section class="panel" style="margin-top:28px">
<div class="head">
<div>
<h2 style="margin:0">My Tasks</h2>
<div class="muted">Semua kegiatan dalam satu tempat.</div>
</div>
<a class="btn" href="/add">＋ Tambah</a>
</div>

<form method="get" class="formgrid">
<div class="field">
<label>Cari tugas</label>
<input name="q" value="{{ q }}" placeholder="Cari judul atau catatan">
</div>
<div class="field">
<label>Tanggal</label>
<input type="date" name="date" value="{{ filter_date }}">
</div>
<div class="field">
<label>Kategori</label>
<select name="category">
<option value="">Semua kategori</option>
{% for c in categories %}
<option value="{{ c }}" {{ 'selected' if filter_category==c else '' }}>{{ c }}</option>
{% endfor %}
</select>
</div>
<div class="field">
<label>Prioritas</label>
<select name="priority">
<option value="">Semua</option>
{% for p in priorities %}
<option value="{{ p }}" {{ 'selected' if filter_priority==p else '' }}>{{ p }}</option>
{% endfor %}
</select>
</div>
<div class="field full">
<label>Status</label>
<select name="status">
<option value="">Semua status</option>
<option value="pending" {{ 'selected' if status=='pending' else '' }}>Belum selesai</option>
<option value="completed" {{ 'selected' if status=='completed' else '' }}>Selesai</option>
</select>
</div>
<div class="full">
<button class="btn">Terapkan filter</button>
<a class="btn light" href="/tasks">Reset</a>
</div>
</form>

<div class="tasklist" style="margin-top:20px">
{% for t in task_list %}
<article class="task {{ 'done' if t.done else '' }}">
<form method="post" action="/toggle/{{ t.id }}">
<input class="check" type="checkbox" {{ 'checked' if t.done else '' }} onchange="this.form.submit()">
</form>
<div class="taskbody">
<div class="tasktitle">{{ t.title }}</div>
<div class="tags">
<span class="tag purple">{{ t.task_date }}</span>
<span class="tag">{{ t.start_time }}–{{ t.end_time }}</span>
<span class="tag">{{ t.category }}</span>
<span class="tag">{{ t.priority }}</span>
</div>
{% if t.notes %}<div class="muted">{{ t.notes }}</div>{% endif %}
<div class="actions">
<a class="mini" href="/edit/{{ t.id }}">✎ Edit</a>
<form method="post" action="/delete/{{ t.id }}" onsubmit="return confirm('Hapus tugas ini?')">
<button class="mini">⌫ Hapus</button>
</form>
</div>
</div>
</article>
{% else %}
<div class="empty">🌱<br>Belum ada tugas yang cocok.</div>
{% endfor %}
</div>
</section>

{% elif page=='form' %}
<section class="panel" style="max-width:700px;margin:28px auto">
<h2>{{ 'Edit kegiatan' if task else 'Tambah kegiatan baru' }}</h2>
<p class="muted">Susun waktumu, satu kegiatan dalam satu waktu.</p>

<form method="post">
<div class="field">
<label>Judul kegiatan *</label>
<input name="title" maxlength="150" required value="{{ task.title if task else '' }}" placeholder="Contoh: Belajar Python">
</div>

<div class="formgrid">
<div class="field">
<label>Tanggal *</label>
<input type="date" name="task_date" required value="{{ task.task_date if task else form_date }}">
</div>
<div class="field">
<label>Kategori</label>
<select name="category">
{% for c in categories %}
<option value="{{ c }}" {{ 'selected' if task and task.category==c else ('selected' if not task and c=='Personal' else '') }}>{{ c }}</option>
{% endfor %}
</select>
</div>
<div class="field">
<label>Jam mulai *</label>
<input type="time" name="start_time" required value="{{ task.start_time if task else '09:00' }}">
</div>
<div class="field">
<label>Jam selesai *</label>
<input type="time" name="end_time" required value="{{ task.end_time if task else '10:00' }}">
</div>
<div class="field full">
<label>Prioritas</label>
<select name="priority">
{% for p in priorities %}
<option value="{{ p }}" {{ 'selected' if task and task.priority==p else ('selected' if not task and p=='Medium' else '') }}>{{ p }}</option>
{% endfor %}
</select>
</div>
<div class="field full">
<label>Catatan</label>
<textarea name="notes" maxlength="2000">{{ task.notes if task else '' }}</textarea>
</div>
</div>
<button class="btn">Simpan kegiatan ✓</button>
<a class="btn light" href="/">Batal</a>
</form>
</section>

{% elif page=='calendar' %}
<section class="panel" style="margin-top:28px">
<div class="head">
<a class="btn light" href="/calendar?month={{ prev_month }}">←</a>
<h3>{{ month_label }}</h3>
<a class="btn light" href="/calendar?month={{ next_month }}">→</a>
</div>

<div class="calendar">
{% for wd in weekdays %}
<div class="weekday">{{ wd }}</div>
{% endfor %}
{% for cell in cells %}
{% if cell.day %}
<a class="day {{ 'selected' if cell.selected else ('today' if cell.today else '') }}" href="/?date={{ cell.date }}">
{{ cell.day }}
{% if cell.has_tasks %}<span class="dot"></span>{% endif %}
</a>
{% else %}
<div class="day"></div>
{% endif %}
{% endfor %}
</div>

<div class="head" style="margin-top:24px">
<div>
<h3>Jadwal {{ selected_date }}</h3>
<div class="muted">Kegiatan pada tanggal terpilih</div>
</div>
<a class="btn" href="/add?date={{ selected_date }}">＋ Tambah</a>
</div>

<div class="tasklist">
{% for t in task_list %}
<article class="task {{ 'done' if t.done else '' }}">
<form method="post" action="/toggle/{{ t.id }}">
<input class="check" type="checkbox" {{ 'checked' if t.done else '' }} onchange="this.form.submit()">
</form>
<div class="taskbody">
<div class="tasktitle">{{ t.title }}</div>
<div class="tags">
<span class="tag purple">{{ t.start_time }}–{{ t.end_time }}</span>
<span class="tag">{{ t.category }}</span>
</div>
<div class="actions"><a class="mini" href="/edit/{{ t.id }}">Edit</a></div>
</div>
</article>
{% else %}
<div class="empty">Tidak ada jadwal pada tanggal ini.</div>
{% endfor %}
</div>
</section>
{% endif %}

<footer>Dayflow · Plan gently, grow daily ✨</footer>
</main>
</div>
</body>
</html>
"""


# =========================================================
# COMMON DATA
# =========================================================

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def common(title):
    today = date.today()
    hour = datetime.now().hour

    greeting = (
        "Selamat pagi" if hour < 11 else
        "Selamat siang" if hour < 15 else
        "Selamat sore" if hour < 18 else
        "Selamat malam"
    )

    months = [
        "", "Januari", "Februari", "Maret", "April", "Mei",
        "Juni", "Juli", "Agustus", "September", "Oktober",
        "November", "Desember"
    ]
    days = [
        "Senin", "Selasa", "Rabu", "Kamis",
        "Jumat", "Sabtu", "Minggu"
    ]

    return dict(
        title=title,
        now=today.isoformat(),
        greeting=greeting,
        today_label=(
            f"{days[today.weekday()]}, {today.day} "
            f"{months[today.month]} {today.year}"
        ),
        categories=CATEGORIES,
        priorities=PRIORITIES,
        lan_url=f"http://{get_local_ip()}:5000"
    )


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def valid_date(value):
    try:
        return date.fromisoformat(value).isoformat()
    except (ValueError, TypeError):
        return None


def find_task(task_id):
    with connect() as db:
        task = db.execute(
            "SELECT * FROM tasks WHERE id=?",
            (task_id,)
        ).fetchone()

    if task is None:
        abort(404)

    return task


def day_tasks(day):
    with connect() as db:
        return db.execute(
            """SELECT * FROM tasks
               WHERE task_date=?
               ORDER BY start_time,id""",
            (day,)
        ).fetchall()


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/")
def home():
    selected = (
        valid_date(request.args.get("date", ""))
        or date.today().isoformat()
    )

    tasks = day_tasks(selected)
    total = len(tasks)
    completed = sum(t["done"] for t in tasks)

    data = common("Dashboard")
    data.update(
        page="home",
        selected_date=selected,
        task_list=tasks,
        total=total,
        completed=completed,
        remaining=total - completed,
        progress=round(completed * 100 / total) if total else 0,
        high_priority=[
            t for t in tasks
            if t["priority"] == "High" and not t["done"]
        ]
    )

    return render_template_string(HTML, **data)


# =========================================================
# ALL TASKS
# =========================================================

@app.route("/tasks")
def tasks_page():
    q = request.args.get("q", "").strip()[:150]
    d = valid_date(request.args.get("date", ""))
    category = request.args.get("category", "")
    priority = request.args.get("priority", "")
    status = request.args.get("status", "")

    sql = "SELECT * FROM tasks WHERE 1=1"
    args = []

    if q:
        sql += " AND (title LIKE ? OR notes LIKE ?)"
        args += [f"%{q}%", f"%{q}%"]

    if d:
        sql += " AND task_date=?"
        args.append(d)

    if category in CATEGORIES:
        sql += " AND category=?"
        args.append(category)
    else:
        category = ""

    if priority in PRIORITIES:
        sql += " AND priority=?"
        args.append(priority)
    else:
        priority = ""

    if status == "completed":
        sql += " AND done=1"
    elif status == "pending":
        sql += " AND done=0"
    else:
        status = ""

    sql += " ORDER BY task_date,start_time,id DESC"

    with connect() as db:
        tasks = db.execute(sql, args).fetchall()

    data = common("My Tasks")
    data.update(
        page="tasks",
        task_list=tasks,
        q=q,
        filter_date=d or "",
        filter_category=category,
        filter_priority=priority,
        status=status
    )

    return render_template_string(HTML, **data)


# =========================================================
# ADD TASK
# =========================================================

@app.route("/add", methods=["GET", "POST"])
def add_task():
    form_date = (
        valid_date(request.args.get("date", ""))
        or date.today().isoformat()
    )

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        d = valid_date(request.form.get("task_date", ""))
        start = request.form.get("start_time", "")
        end = request.form.get("end_time", "")
        category = request.form.get("category", "Personal")
        priority = request.form.get("priority", "Medium")
        notes = request.form.get("notes", "").strip()

        if not title or len(title) > 150 or not d:
            abort(400, "Judul atau tanggal tidak valid.")

        try:
            datetime.strptime(start, "%H:%M")
            datetime.strptime(end, "%H:%M")
        except ValueError:
            abort(400, "Jam tidak valid.")

        if end <= start:
            abort(400, "Jam selesai harus setelah jam mulai.")

        if category not in CATEGORIES:
            category = "Personal"

        if priority not in PRIORITIES:
            priority = "Medium"

        with connect() as db:
            db.execute(
                """INSERT INTO tasks
                (title,task_date,start_time,end_time,category,priority,notes,done)
                VALUES (?,?,?,?,?,?,?,0)""",
                (title, d, start, end, category, priority, notes)
            )

        return redirect(url_for("home", date=d))

    data = common("Tambah Kegiatan")
    data.update(page="form", task=None, form_date=form_date)

    return render_template_string(HTML, **data)


# =========================================================
# EDIT TASK
# =========================================================

@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    task = find_task(task_id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        d = valid_date(request.form.get("task_date", ""))
        start = request.form.get("start_time", "")
        end = request.form.get("end_time", "")
        category = request.form.get("category", "Personal")
        priority = request.form.get("priority", "Medium")
        notes = request.form.get("notes", "").strip()

        if not title or len(title) > 150 or not d:
            abort(400, "Judul atau tanggal tidak valid.")

        try:
            datetime.strptime(start, "%H:%M")
            datetime.strptime(end, "%H:%M")
        except ValueError:
            abort(400, "Jam tidak valid.")

        if end <= start:
            abort(400, "Jam selesai harus setelah jam mulai.")

        if category not in CATEGORIES:
            category = "Personal"

        if priority not in PRIORITIES:
            priority = "Medium"

        with connect() as db:
            db.execute(
                """UPDATE tasks
                SET title=?,task_date=?,start_time=?,
                    end_time=?,category=?,priority=?,notes=?
                WHERE id=?""",
                (title, d, start, end, category, priority, notes, task_id)
            )

        return redirect(url_for("home", date=d))

    data = common("Edit Kegiatan")
    data.update(
        page="form",
        task=task,
        form_date=task["task_date"]
    )

    return render_template_string(HTML, **data)


# =========================================================
# TOGGLE TASK STATUS
# =========================================================

@app.route("/toggle/<int:task_id>", methods=["POST"])
def toggle_task(task_id):
    task = find_task(task_id)

    with connect() as db:
        db.execute(
            "UPDATE tasks SET done=? WHERE id=?",
            (0 if task["done"] else 1, task_id)
        )

    return redirect(request.referrer or url_for("home"))


# =========================================================
# DELETE TASK
# =========================================================

@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    find_task(task_id)

    with connect() as db:
        db.execute(
            "DELETE FROM tasks WHERE id=?",
            (task_id,)
        )

    return redirect(request.referrer or url_for("home"))


# =========================================================
# CALENDAR
# =========================================================

@app.route("/calendar")
def calendar_page():
    raw = request.args.get(
        "month",
        date.today().strftime("%Y-%m")
    )

    try:
        year, month = map(int, raw.split("-"))

        if not 1 <= month <= 12:
            raise ValueError

        date(year, month, 1)

    except (ValueError, TypeError):
        year = date.today().year
        month = date.today().month

    selected = date.today().isoformat()

    first_weekday, days_in_month = calendar.monthrange(year, month)

    prev_y, prev_m = (
        (year - 1, 12) if month == 1
        else (year, month - 1)
    )

    next_y, next_m = (
        (year + 1, 1) if month == 12
        else (year, month + 1)
    )

    with connect() as db:
        dates = {
            r["task_date"]
            for r in db.execute(
                """SELECT DISTINCT task_date FROM tasks
                WHERE task_date LIKE ?""",
                (f"{year:04d}-{month:02d}-%",)
            ).fetchall()
        }

    cells = [{"day": None} for _ in range(first_weekday)]

    for n in range(1, days_in_month + 1):
        d = date(year, month, n).isoformat()

        cells.append({
            "day": n,
            "date": d,
            "selected": d == selected,
            "today": d == date.today().isoformat(),
            "has_tasks": d in dates
        })

    while len(cells) % 7:
        cells.append({"day": None})

    tasks = day_tasks(selected)

    data = common("Calendar")

    months = [
        "Januari", "Februari", "Maret", "April",
        "Mei", "Juni", "Juli", "Agustus",
        "September", "Oktober", "November", "Desember"
    ]

    data.update(
        page="calendar",
        cells=cells,
        task_list=tasks,
        selected_date=selected,
        month_label=f"{months[month - 1]} {year}",
        prev_month=f"{prev_y:04d}-{prev_m:02d}",
        next_month=f"{next_y:04d}-{next_m:02d}",
        weekdays=["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
    )

    return render_template_string(HTML, **data)


# =========================================================
# LOCAL NETWORK + AUTO OPEN BROWSER
# =========================================================

def open_browser():
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = 5000

    local_ip = get_local_ip()

    print("\n" + "=" * 55)
    print("             DAYFLOW DAILY PLANNER")
    print("=" * 55)
    print(f"LOKAL KOMPUTER : http://127.0.0.1:{PORT}")
    print(f"JARINGAN LAN   : http://{local_ip}:{PORT}")
    print("=" * 55)
    print("Browser akan terbuka secara otomatis.")
    print("Untuk HP, gunakan alamat JARINGAN LAN.")
    print("Pastikan HP dan komputer memakai Wi-Fi yang sama.")
    print("Tekan CTRL+C untuk menghentikan server.")
    print("=" * 55 + "\n")

    threading.Timer(1.5, open_browser).start()

    app.run(
        host=HOST,
        port=PORT,
        debug=False,
        use_reloader=False
    )
