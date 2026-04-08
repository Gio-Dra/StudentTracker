from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3
from datetime import datetime
import json

app = Flask(__name__)
DB_NAME = "engagement.db"

# F1 drivers used only as names in the roster
STUDENTS = [
    "Max Verstappen",
    "Lewis Hamilton",
    "Charles Leclerc",
    "Lando Norris",
    "George Russell",
    "Carlos Sainz",
    "Sergio Perez",
    "Fernando Alonso",
    "Oscar Piastri",
    "Pierre Gasly",
    "Esteban Ocon",
    "Yuki Tsunoda",
    "Alex Albon",
    "Valtteri Bottas",
    "Lance Stroll",
    "Kevin Magnussen",
    "Nico Hulkenberg",
    "Daniel Ricciardo",
    "Logan Sargeant"
]

BASE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Oswald:wght@300;400;500;700&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --erau-navy: #0c2340;
            --erau-navy-2: #13335c;
            --erau-blue: #0072ce;
            --erau-blue-dark: #055eba;
            --erau-gold: #f2a900;
            --erau-ice: #e9f2fb;
            --erau-border: #c9d7e6;
            --erau-text: #17324d;
            --erau-muted: #5d7187;
            --erau-white: #ffffff;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            background:
                linear-gradient(180deg, rgba(12,35,64,0.98) 0px, rgba(12,35,64,0.98) 86px, #eef3f8 86px, #f7f9fc 100%);
            color: var(--erau-text);
            font-family: 'Inter', Arial, sans-serif;
        }

        a {
            text-decoration: none;
        }

        .topbar {
            background: #091a30;
            color: rgba(255,255,255,0.85);
            font-size: 0.84rem;
        }

        .topbar a {
            color: rgba(255,255,255,0.88);
            margin-right: 1.25rem;
        }

        .site-header {
            background: var(--erau-navy);
            border-bottom: 1px solid rgba(255,255,255,0.12);
            box-shadow: 0 8px 22px rgba(8, 24, 44, 0.18);
        }

        .brand-wrap {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .brand-mark {
            width: 52px;
            height: 52px;
            border-radius: 8px;
            background: linear-gradient(180deg, var(--erau-blue) 0%, var(--erau-blue-dark) 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-family: 'Oswald', sans-serif;
            font-size: 1.2rem;
            letter-spacing: 0.05em;
            box-shadow: inset 0 0 0 1px rgba(255,255,255,0.18);
        }

        .brand-text {
            color: white;
            line-height: 1.1;
        }

        .brand-kicker {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.13em;
            color: rgba(255,255,255,0.72);
            margin-bottom: 0.18rem;
        }

        .brand-title {
            font-family: 'Oswald', sans-serif;
            font-size: 1.6rem;
            letter-spacing: 0.02em;
            margin: 0;
        }

        .brand-subtitle {
            margin: 0.15rem 0 0;
            color: rgba(255,255,255,0.78);
            font-size: 0.9rem;
        }

        .header-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
            justify-content: flex-end;
        }

        .btn-erau,
        .btn-erau-outline,
        .btn-erau-light {
            border-radius: 0;
            font-weight: 700;
            padding: 0.65rem 1rem;
            font-size: 0.92rem;
            transition: 0.18s ease;
            box-shadow: none;
        }

        .btn-erau {
            background: var(--erau-blue);
            color: white;
            border: 1px solid var(--erau-blue);
        }

        .btn-erau:hover {
            background: var(--erau-blue-dark);
            border-color: var(--erau-blue-dark);
            color: white;
        }

        .btn-erau-outline {
            background: transparent;
            color: white;
            border: 1px solid rgba(255,255,255,0.45);
        }

        .btn-erau-outline:hover {
            background: rgba(255,255,255,0.08);
            border-color: white;
            color: white;
        }

        .btn-erau-light {
            background: white;
            color: var(--erau-navy);
            border: 1px solid white;
        }

        .btn-erau-light:hover {
            background: #edf4fb;
            color: var(--erau-navy);
            border-color: #edf4fb;
        }

        .page-shell {
            padding: 2rem 0 3rem;
        }

        .hero-panel,
        .content-panel,
        .chart-panel,
        .table-panel,
        .metric-card {
            background: white;
            border: 1px solid var(--erau-border);
            box-shadow: 0 10px 30px rgba(18, 47, 87, 0.08);
        }

        .hero-panel {
            padding: 2rem;
            border-top: 6px solid var(--erau-blue);
            margin-bottom: 1.5rem;
        }

        .eyebrow {
            display: inline-block;
            background: #e8f1fb;
            color: var(--erau-blue-dark);
            border: 1px solid #bfd7f2;
            padding: 0.35rem 0.7rem;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.95rem;
        }

        .hero-title {
            font-family: 'Oswald', sans-serif;
            font-size: clamp(2rem, 4vw, 3.2rem);
            line-height: 1.02;
            color: var(--erau-navy);
            margin-bottom: 0.6rem;
        }

        .hero-copy,
        .subtle {
            color: var(--erau-muted);
            font-size: 1rem;
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
        }

        .metric-card {
            padding: 1rem 1.1rem;
        }

        .metric-label {
            color: var(--erau-muted);
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }

        .metric-number {
            color: var(--erau-navy);
            font-size: 2rem;
            line-height: 1;
            font-weight: 800;
            margin-top: 0.4rem;
        }

        .content-panel {
            padding: 1.35rem;
            margin-bottom: 1.25rem;
        }

        .section-title {
            font-family: 'Oswald', sans-serif;
            color: var(--erau-navy);
            margin-bottom: 1rem;
            font-size: 1.55rem;
        }

        .table-wrap {
            border: 1px solid var(--erau-border);
            overflow: hidden;
            background: white;
        }

        .table-erau {
            margin: 0;
            vertical-align: middle;
        }

        .table-erau thead th {
            background: var(--erau-navy);
            color: white;
            border-color: rgba(255,255,255,0.15);
            font-weight: 700;
            font-size: 0.92rem;
            white-space: nowrap;
        }

        .table-erau tbody td {
            border-color: #dde7f1;
            color: var(--erau-text);
        }

        .table-erau tbody tr:nth-child(even) {
            background: #f8fbfe;
        }

        .student-cell {
            font-weight: 700;
            min-width: 210px;
        }

        .form-control,
        .form-select {
            border-radius: 0;
            border-color: #bccedf;
            min-height: 44px;
        }

        .form-control:focus,
        .form-select:focus,
        .form-check-input:focus {
            border-color: var(--erau-blue);
            box-shadow: 0 0 0 0.2rem rgba(0,114,206,0.15);
        }

        .form-check-input {
            transform: scale(1.15);
            border-radius: 0;
            border-color: #7f9cba;
        }

        .form-check-input:checked {
            background-color: var(--erau-blue);
            border-color: var(--erau-blue);
        }

        .sticky-actions {
            position: sticky;
            bottom: 1rem;
            z-index: 30;
        }

        .action-bar {
            background: rgba(12,35,64,0.96);
            border: 1px solid rgba(255,255,255,0.12);
            padding: 0.9rem;
            display: flex;
            justify-content: flex-end;
            gap: 0.75rem;
            box-shadow: 0 10px 25px rgba(10, 28, 50, 0.22);
        }

        .chart-panel {
            padding: 1rem;
            height: 100%;
        }

        canvas {
            width: 100% !important;
            background: #fbfdff;
            border: 1px solid #d9e6f2;
            padding: 0.5rem;
        }

        .records-note {
            color: var(--erau-muted);
        }

        .footer-note {
            color: #6a7f95;
            font-size: 0.85rem;
            text-align: center;
            margin-top: 2rem;
        }

        @media (max-width: 991px) {
            .header-actions {
                justify-content: flex-start;
                margin-top: 1rem;
            }
        }

        @media (max-width: 767px) {
            .hero-panel {
                padding: 1.35rem;
            }

            .page-shell {
                padding-top: 1.25rem;
            }

            .action-bar {
                flex-direction: column;
            }

            .action-bar .btn {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="topbar py-2">
        <div class="container d-flex flex-wrap gap-3">
            <span>Campus Engagement Tools</span>
            <span>Prescott Style Interface</span>
            <span>Internal Use</span>
        </div>
    </div>

    <header class="site-header py-3">
        <div class="container">
            <div class="row align-items-center g-3">
                <div class="col-lg-7">
                    <div class="brand-wrap">
                        <div class="brand-mark">PC</div>
                        <div class="brand-text">
                            <div class="brand-kicker">Engagement System</div>
                            <h1 class="brand-title">Prescott Classroom Tracker</h1>
                            <p class="brand-subtitle">Structured entry, dashboard summaries and session records</p>
                        </div>
                    </div>
                </div>
                <div class="col-lg-5">
                    <div class="header-actions">
                        <a href="/" class="btn btn-erau-light">Entry</a>
                        <a href="/dashboard" class="btn btn-erau">Dashboard</a>
                        <a href="/records" class="btn btn-erau-outline">Records</a>
                    </div>
                </div>
            </div>
        </div>
    </header>

    <main class="page-shell">
        <div class="container">
            {{ content|safe }}
            <div class="footer-note">Styled to match the same navy / light-blue Prescott site feel.</div>
        </div>
    </main>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

INDEX_HTML = """
<div class="hero-panel">
    <div class="row g-4 align-items-end">
        <div class="col-lg-8">
            <div class="eyebrow">Session Entry</div>
            <div class="hero-title">Track engagement with a Prescott-style layout</div>
            <p class="hero-copy mb-0">
                Enter attendance, engagement, participation and notes for a single class session.
                The names below are your requested roster names, but the system styling stays aligned with the Prescott site look.
            </p>
        </div>
        <div class="col-lg-4">
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">Students Loaded</div>
                    <div class="metric-number">{{ students|length }}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Today's Date</div>
                    <div class="metric-number" style="font-size:1.15rem; line-height:1.25;">{{ today }}</div>
                </div>
            </div>
        </div>
    </div>
</div>

<form method="POST">
    <div class="content-panel">
        <div class="row g-3 align-items-end">
            <div class="col-md-4">
                <label class="form-label fw-semibold">Session Date</label>
                <input type="date" class="form-control" name="session_date" value="{{ today }}" required>
            </div>
            <div class="col-md-8">
                <label class="form-label fw-semibold">Guidance</label>
                <div class="content-panel mb-0" style="padding:0.9rem 1rem; background:#f8fbff; border-color:#d7e4f1;">
                    <div class="subtle">
                        Engagement = attentive / following along. Participation = active contribution. Use notes for quick context.
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="table-wrap">
        <div class="table-responsive">
            <table class="table table-erau align-middle mb-0">
                <thead>
                    <tr>
                        <th>Student</th>
                        <th class="text-center">1st Half</th>
                        <th class="text-center">2nd Half</th>
                        <th class="text-center">Participated</th>
                        <th class="text-center">Q / Comments</th>
                        <th class="text-center">Absent</th>
                        <th>Notes</th>
                    </tr>
                </thead>
                <tbody>
                    {% for student in students %}
                    <tr>
                        <td class="student-cell">{{ student['full_name'] }}</td>
                        <td class="text-center"><input class="form-check-input" type="checkbox" name="engaged_first_{{ student['id'] }}"></td>
                        <td class="text-center"><input class="form-check-input" type="checkbox" name="engaged_second_{{ student['id'] }}"></td>
                        <td class="text-center"><input class="form-check-input" type="checkbox" name="participated_{{ student['id'] }}"></td>
                        <td class="text-center"><input class="form-control form-control-sm" type="number" min="0" value="0" name="questions_{{ student['id'] }}"></td>
                        <td class="text-center"><input class="form-check-input" type="checkbox" name="absent_{{ student['id'] }}"></td>
                        <td><input class="form-control form-control-sm" type="text" name="notes_{{ student['id'] }}" placeholder="Optional note"></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <div class="sticky-actions mt-4">
        <div class="action-bar">
            <a href="/dashboard" class="btn btn-erau-outline">View Dashboard</a>
            <button type="submit" class="btn btn-erau">Save Session</button>
        </div>
    </div>
</form>
"""

DASHBOARD_HTML = """
<div class="hero-panel">
    <div class="row g-4 align-items-end">
        <div class="col-lg-7">
            <div class="eyebrow">Dashboard</div>
            <div class="hero-title">Session analytics dashboard</div>
            <p class="hero-copy mb-0">Plots attendance, participation, engagement and question activity directly from the database.</p>
        </div>
        <div class="col-lg-5">
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">Sessions</div>
                    <div class="metric-number">{{ summary.sessions }}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Avg Attendance</div>
                    <div class="metric-number">{{ summary.avg_attendance }}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Avg Participation</div>
                    <div class="metric-number">{{ summary.avg_participation }}%</div>
                </div>
            </div>
        </div>
    </div>
</div>

{% if labels %}
<div class="row g-4">
    <div class="col-12">
        <div class="chart-panel">
            <h3 class="section-title">Attendance vs Participation</h3>
            <canvas id="lineChart" height="115"></canvas>
        </div>
    </div>
    <div class="col-lg-6">
        <div class="chart-panel">
            <h3 class="section-title">Average Engagement Score</h3>
            <canvas id="engagementChart" height="150"></canvas>
        </div>
    </div>
    <div class="col-lg-6">
        <div class="chart-panel">
            <h3 class="section-title">Questions / Comments</h3>
            <canvas id="questionsChart" height="150"></canvas>
        </div>
    </div>
</div>
{% else %}
<div class="content-panel">
    <div class="alert alert-primary mb-0">No session data yet. Go to the entry page and save a class session first.</div>
</div>
{% endif %}

{% if labels %}
<script>
const labels = {{ labels|safe }};
const attendance = {{ attendance|safe }};
const participation = {{ participation|safe }};
const engagement = {{ engagement|safe }};
const questions = {{ questions|safe }};

const commonLegend = {
    labels: {
        color: '#17324d',
        font: { family: 'Inter', weight: '600' }
    }
};

const commonGridColor = 'rgba(12, 35, 64, 0.10)';
const commonTickColor = '#48627b';

new Chart(document.getElementById('lineChart'), {
    type: 'line',
    data: {
        labels,
        datasets: [
            {
                label: 'Attendance %',
                data: attendance,
                borderColor: '#0072ce',
                backgroundColor: 'rgba(0,114,206,0.12)',
                tension: 0.25,
                borderWidth: 3,
                pointRadius: 4,
                pointBackgroundColor: '#0072ce',
                fill: false
            },
            {
                label: 'Participation %',
                data: participation,
                borderColor: '#0c2340',
                backgroundColor: 'rgba(12,35,64,0.12)',
                tension: 0.25,
                borderWidth: 3,
                pointRadius: 4,
                pointBackgroundColor: '#0c2340',
                fill: false
            }
        ]
    },
    options: {
        responsive: true,
        plugins: { legend: commonLegend },
        scales: {
            x: { ticks: { color: commonTickColor }, grid: { color: commonGridColor } },
            y: {
                min: 0,
                max: 100,
                ticks: { color: commonTickColor },
                grid: { color: commonGridColor }
            }
        }
    }
});

new Chart(document.getElementById('engagementChart'), {
    type: 'bar',
    data: {
        labels,
        datasets: [{
            label: 'Avg Engagement %',
            data: engagement,
            backgroundColor: '#0072ce',
            borderColor: '#055eba',
            borderWidth: 1.5
        }]
    },
    options: {
        plugins: { legend: commonLegend },
        scales: {
            x: { ticks: { color: commonTickColor }, grid: { color: commonGridColor } },
            y: {
                min: 0,
                max: 100,
                ticks: { color: commonTickColor },
                grid: { color: commonGridColor }
            }
        }
    }
});

new Chart(document.getElementById('questionsChart'), {
    type: 'bar',
    data: {
        labels,
        datasets: [{
            label: 'Questions / Comments',
            data: questions,
            backgroundColor: '#0c2340',
            borderColor: '#08182d',
            borderWidth: 1.5
        }]
    },
    options: {
        plugins: { legend: commonLegend },
        scales: {
            x: { ticks: { color: commonTickColor }, grid: { color: commonGridColor } },
            y: {
                beginAtZero: true,
                ticks: { color: commonTickColor },
                grid: { color: commonGridColor }
            }
        }
    }
});
</script>
{% endif %}
"""

RECORDS_HTML = """
<div class="hero-panel">
    <div class="eyebrow">Records</div>
    <div class="hero-title">Observation records</div>
    <p class="hero-copy mb-0">Use this page to verify exactly what was stored in the database.</p>
</div>

<div class="content-panel">
    <div class="records-note mb-3">All sessions are shown newest first.</div>
    <div class="table-wrap">
        <div class="table-responsive">
            <table class="table table-erau align-middle mb-0">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Student</th>
                        <th>1st Half</th>
                        <th>2nd Half</th>
                        <th>Participated</th>
                        <th>Q / Comments</th>
                        <th>Absent</th>
                        <th>Notes</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in rows %}
                    <tr>
                        <td>{{ row['session_date'] }}</td>
                        <td class="student-cell">{{ row['full_name'] }}</td>
                        <td>{{ row['engaged_first_half'] }}</td>
                        <td>{{ row['engaged_second_half'] }}</td>
                        <td>{{ row['participated'] }}</td>
                        <td>{{ row['questions_comments'] }}</td>
                        <td>{{ row['absent'] }}</td>
                        <td>{{ row['notes'] or '' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
"""


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL UNIQUE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS class_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_date TEXT NOT NULL UNIQUE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS observations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        session_id INTEGER NOT NULL,
        engaged_first_half INTEGER NOT NULL DEFAULT 0,
        engaged_second_half INTEGER NOT NULL DEFAULT 0,
        participated INTEGER NOT NULL DEFAULT 0,
        questions_comments INTEGER NOT NULL DEFAULT 0,
        absent INTEGER NOT NULL DEFAULT 0,
        notes TEXT,
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (session_id) REFERENCES class_sessions(id),
        UNIQUE(student_id, session_id)
    )
    """)

    conn.commit()
    conn.close()


def seed_students():
    conn = get_db_connection()
    cur = conn.cursor()
    for name in STUDENTS:
        cur.execute("INSERT OR IGNORE INTO students (full_name) VALUES (?)", (name,))
    conn.commit()
    conn.close()


def render_page(title, content, **context):
    return render_template_string(
        BASE_HTML,
        title=title,
        content=render_template_string(content, **context)
    )


@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        session_date = request.form['session_date']
        cur.execute("INSERT OR IGNORE INTO class_sessions (session_date) VALUES (?)", (session_date,))
        conn.commit()

        session_row = cur.execute(
            "SELECT id FROM class_sessions WHERE session_date = ?",
            (session_date,)
        ).fetchone()
        session_id = session_row['id']

        students = cur.execute("SELECT * FROM students ORDER BY full_name").fetchall()

        for student in students:
            sid = student['id']
            engaged_first = 1 if request.form.get(f'engaged_first_{sid}') else 0
            engaged_second = 1 if request.form.get(f'engaged_second_{sid}') else 0
            participated = 1 if request.form.get(f'participated_{sid}') else 0
            absent = 1 if request.form.get(f'absent_{sid}') else 0
            questions = int(request.form.get(f'questions_{sid}', '0') or 0)
            notes = request.form.get(f'notes_{sid}', '').strip()

            cur.execute("""
                INSERT INTO observations (
                    student_id,
                    session_id,
                    engaged_first_half,
                    engaged_second_half,
                    participated,
                    questions_comments,
                    absent,
                    notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(student_id, session_id) DO UPDATE SET
                    engaged_first_half = excluded.engaged_first_half,
                    engaged_second_half = excluded.engaged_second_half,
                    participated = excluded.participated,
                    questions_comments = excluded.questions_comments,
                    absent = excluded.absent,
                    notes = excluded.notes
            """, (sid, session_id, engaged_first, engaged_second, participated, questions, absent, notes))

        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))

    students = cur.execute("SELECT * FROM students ORDER BY full_name").fetchall()
    conn.close()

    return render_page(
        'Engagement Tracker',
        INDEX_HTML,
        students=students,
        today=datetime.today().strftime('%Y-%m-%d')
    )


@app.route('/records')
def records():
    conn = get_db_connection()
    cur = conn.cursor()
    rows = cur.execute("""
        SELECT
            cs.session_date,
            s.full_name,
            o.engaged_first_half,
            o.engaged_second_half,
            o.participated,
            o.questions_comments,
            o.absent,
            o.notes
        FROM observations o
        JOIN students s ON s.id = o.student_id
        JOIN class_sessions cs ON cs.id = o.session_id
        ORDER BY cs.session_date DESC, s.full_name ASC
    """).fetchall()
    conn.close()
    return render_page('Records', RECORDS_HTML, rows=rows)


@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    cur = conn.cursor()

    rows = cur.execute("""
        SELECT
            cs.session_date,
            COUNT(*) AS total_students,
            SUM(CASE WHEN o.absent = 0 THEN 1 ELSE 0 END) AS present_count,
            SUM(o.participated) AS participated_count,
            SUM(o.questions_comments) AS total_questions,
            AVG((o.engaged_first_half + o.engaged_second_half) * 50.0) AS avg_engagement_percent
        FROM observations o
        JOIN class_sessions cs ON cs.id = o.session_id
        GROUP BY cs.session_date
        ORDER BY cs.session_date ASC
    """).fetchall()
    conn.close()

    labels = []
    attendance = []
    participation = []
    engagement = []
    questions = []

    for row in rows:
        total = row['total_students'] or 1
        labels.append(row['session_date'])
        attendance.append(round(100.0 * row['present_count'] / total, 2))
        participation.append(round(100.0 * row['participated_count'] / total, 2))
        engagement.append(round(row['avg_engagement_percent'] or 0, 2))
        questions.append(row['total_questions'] or 0)

    summary = {
        'sessions': len(rows),
        'avg_attendance': round(sum(attendance) / len(attendance), 1) if attendance else 0,
        'avg_participation': round(sum(participation) / len(participation), 1) if participation else 0,
    }

    return render_page(
        'Dashboard',
        DASHBOARD_HTML,
        labels=json.dumps(labels),
        attendance=json.dumps(attendance),
        participation=json.dumps(participation),
        engagement=json.dumps(engagement),
        questions=json.dumps(questions),
        summary=summary
    )


if __name__ == '__main__':
    init_db()
    seed_students()
    app.run(host='0.0.0.0', port=5000, debug=False)
