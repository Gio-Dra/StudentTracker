from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3
from datetime import datetime
import json

app = Flask(__name__)
DB_NAME = "engagement.db"

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
    <link href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <style>
        :root {
            --erau-navy: #102a43;
            --erau-navy-2: #163a63;
            --erau-blue: #1f6fb2;
            --erau-blue-dark: #17598f;
            --erau-light: #eef4fa;
            --erau-border: #d4dfeb;
            --erau-text: #18324a;
            --erau-muted: #61758a;
            --erau-white: #ffffff;
            --erau-green: #2f7d4a;
            --erau-orange: #cc7a00;
            --erau-shadow: 0 8px 22px rgba(16, 42, 67, 0.08);
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            background:
                linear-gradient(
                    180deg,
                    rgba(16, 42, 67, 0.98) 0px,
                    rgba(16, 42, 67, 0.98) 92px,
                    #eef3f8 92px,
                    #f7f9fc 100%
                );
            color: var(--erau-text);
            font-family: 'Inter', Arial, sans-serif;
        }

        a {
            text-decoration: none;
        }

        .topbar {
            background: #0b1f33;
            color: rgba(255,255,255,0.82);
            font-size: 0.82rem;
            border-bottom: 1px solid rgba(255,255,255,0.08);
        }

        .site-header {
            background: var(--erau-navy);
            box-shadow: 0 8px 24px rgba(8, 24, 44, 0.16);
        }

        .brand-wrap {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .brand-mark {
            width: 56px;
            height: 56px;
            border-radius: 8px;
            background: linear-gradient(180deg, var(--erau-blue) 0%, var(--erau-blue-dark) 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-family: 'Oswald', sans-serif;
            font-size: 1.15rem;
            letter-spacing: 0.06em;
            box-shadow: inset 0 0 0 1px rgba(255,255,255,0.16);
        }

        .brand-text {
            color: white;
            line-height: 1.1;
        }

        .brand-kicker {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.14em;
            color: rgba(255,255,255,0.72);
            margin-bottom: 0.18rem;
        }

        .brand-title {
            margin: 0;
            font-family: 'Oswald', sans-serif;
            font-size: 1.7rem;
            letter-spacing: 0.02em;
        }

        .brand-subtitle {
            margin: 0.2rem 0 0;
            color: rgba(255,255,255,0.78);
            font-size: 0.92rem;
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
            color: white;
            border-color: white;
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
        .metric-card,
        .table-shell {
            background: white;
            border: 1px solid var(--erau-border);
            box-shadow: var(--erau-shadow);
        }

        .hero-panel {
            padding: 2rem;
            border-top: 6px solid var(--erau-blue);
            margin-bottom: 1.5rem;
        }

        .eyebrow {
            display: inline-block;
            background: #e7f0fa;
            color: var(--erau-blue-dark);
            border: 1px solid #bfd2e7;
            padding: 0.38rem 0.72rem;
            font-size: 0.78rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 1rem;
        }

        .hero-title {
            font-family: 'Oswald', sans-serif;
            font-size: clamp(2rem, 4vw, 3.15rem);
            line-height: 1.02;
            color: var(--erau-navy);
            margin-bottom: 0.65rem;
        }

        .hero-copy,
        .subtle {
            color: var(--erau-muted);
            font-size: 1rem;
            line-height: 1.6;
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
        }

        .metric-card {
            padding: 1rem 1.1rem;
            min-height: 118px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .metric-label {
            color: var(--erau-muted);
            font-size: 0.82rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }

        .metric-number {
            color: var(--erau-navy);
            font-size: 2rem;
            line-height: 1.05;
            font-weight: 800;
            margin-top: 0.42rem;
        }

        .content-panel {
            padding: 1.35rem;
            margin-bottom: 1.25rem;
        }

        .section-title {
            font-family: 'Oswald', sans-serif;
            color: var(--erau-navy);
            margin-bottom: 0.85rem;
            font-size: 1.65rem;
            letter-spacing: 0.01em;
        }

        .section-copy {
            color: var(--erau-muted);
            margin-bottom: 1rem;
            line-height: 1.55;
        }

        .table-shell {
            overflow: hidden;
        }

        .table-wrap {
            border-top: 1px solid var(--erau-border);
            background: white;
        }

        .table-erau {
            margin: 0;
            vertical-align: middle;
        }

        .table-erau thead th {
            background: var(--erau-navy);
            color: white;
            border-color: rgba(255,255,255,0.12);
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
            box-shadow: 0 0 0 0.2rem rgba(31,111,178,0.15);
        }

        .form-check-input {
            transform: scale(1.12);
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
            background: rgba(16, 42, 67, 0.96);
            border: 1px solid rgba(255,255,255,0.12);
            padding: 0.95rem;
            display: flex;
            justify-content: flex-end;
            gap: 0.75rem;
            box-shadow: 0 10px 25px rgba(10, 28, 50, 0.22);
        }

        .chart-panel {
            padding: 1.15rem;
            height: 100%;
        }

        .chart-box {
            position: relative;
            height: 340px;
        }

        .chart-box-small {
            position: relative;
            height: 320px;
        }

        canvas {
            width: 100% !important;
            height: 100% !important;
            background: #fbfdff;
            border: 1px solid #d9e6f2;
            padding: 0.55rem;
        }

        .records-note {
            color: var(--erau-muted);
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

            .chart-box,
            .chart-box-small {
                height: 280px;
            }
        }
    </style>
</head>
<body>
    <div class="topbar py-2">
        <div class="container d-flex flex-wrap gap-3">
            <span>Center for Teaching & Learning Excellence</span>
            <span>CEC 320</span>
            <span>Students-as-Partners</span>
        </div>
    </div>

    <header class="site-header py-3">
        <div class="container">
            <div class="row align-items-center g-3">
                <div class="col-lg-7">
                    <div class="brand-wrap">
                        <div class="brand-mark">CTLE</div>
                        <div class="brand-text">
                            <div class="brand-kicker">Prescott Teaching Dashboard</div>
                            <h1 class="brand-title">CEC 320 Student Partner Tracker</h1>
                            <p class="brand-subtitle">Observation entry, dashboard summaries, and saved session records</p>
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
            <div class="eyebrow">Observation Entry</div>
            <div class="hero-title">CEC 320 classroom observation form</div>
            <p class="hero-copy mb-0">
                Log attendance, engagement, participation, and short notes for each class session.
                This layout is styled for a clean CTLE / Prescott presentation while keeping your database workflow simple.
            </p>
        </div>
        <div class="col-lg-4">
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">Students Loaded</div>
                    <div class="metric-number">{{ students|length }}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Session Date</div>
                    <div class="metric-number" style="font-size:1.1rem; line-height:1.35;">{{ today }}</div>
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
                <label class="form-label fw-semibold">Observation Guidance</label>
                <div class="content-panel mb-0" style="padding:0.9rem 1rem; background:#f8fbff; border-color:#d7e4f1;">
                    <div class="subtle">
                        Engagement = attentive / following class. Participation = visible contribution.
                        Use notes for pacing, confusion points, classroom energy, or teaching observations.
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="table-shell">
        <div class="content-panel" style="margin-bottom:0; border-bottom:none; box-shadow:none;">
            <h3 class="section-title mb-2">Student session inputs</h3>
            <div class="section-copy mb-0">
                Enter one row per student for the selected session. The F1 names are just your roster labels.
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
            <div class="hero-title">CEC 320 student partner dashboard</div>
            <p class="hero-copy mb-0">
                Tracks attendance, participation, engagement, and classroom interaction trends
                to support CTLE Students-as-Partners reflection and instructional improvement.
            </p>
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
                <div class="metric-card">
                    <div class="metric-label">Avg Engagement</div>
                    <div class="metric-number">{{ summary.avg_engagement }}%</div>
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
            <div class="section-copy">
                Attendance shows who was present. Participation shows who actively contributed.
                The taller chart area fixes the flattened look from before.
            </div>
            <div class="chart-box">
                <canvas id="lineChart"></canvas>
            </div>
        </div>
    </div>

    <div class="col-lg-6">
        <div class="chart-panel">
            <h3 class="section-title">Average Engagement Score</h3>
            <div class="section-copy">
                Engagement combines first-half and second-half observation checks into a 0 to 100 scale.
            </div>
            <div class="chart-box-small">
                <canvas id="engagementChart"></canvas>
            </div>
        </div>
    </div>

    <div class="col-lg-6">
        <div class="chart-panel">
            <h3 class="section-title">Questions / Comments Activity</h3>
            <div class="section-copy">
                This tracks visible student questions or comment interactions during each observed session.
            </div>
            <div class="chart-box-small">
                <canvas id="questionsChart"></canvas>
            </div>
        </div>
    </div>
</div>
{% else %}
<div class="content-panel">
    <div class="alert alert-primary mb-0">
        No session data yet. Go to the entry page and save a class session first.
    </div>
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
        color: '#18324a',
        font: {
            family: 'Inter',
            weight: '600'
        }
    }
};

const commonGridColor = 'rgba(16, 42, 67, 0.10)';
const commonTickColor = '#4f667d';

new Chart(document.getElementById('lineChart'), {
    type: 'line',
    data: {
        labels,
        datasets: [
            {
                label: 'Attendance %',
                data: attendance,
                borderColor: '#1f6fb2',
                backgroundColor: 'rgba(31,111,178,0.10)',
                tension: 0.25,
                borderWidth: 3,
                pointRadius: 4,
                pointHoverRadius: 5,
                pointBackgroundColor: '#1f6fb2',
                fill: false
            },
            {
                label: 'Participation %',
                data: participation,
                borderColor: '#cc7a00',
                backgroundColor: 'rgba(204,122,0,0.10)',
                tension: 0.25,
                borderWidth: 3,
                pointRadius: 4,
                pointHoverRadius: 5,
                pointBackgroundColor: '#cc7a00',
                fill: false
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
            padding: 12
        },
        plugins: {
            legend: commonLegend
        },
        scales: {
            x: {
                ticks: {
                    color: commonTickColor
                },
                grid: {
                    color: commonGridColor
                }
            },
            y: {
                min: 0,
                max: 100,
                ticks: {
                    color: commonTickColor
                },
                grid: {
                    color: commonGridColor
                }
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
            backgroundColor: '#2f7d4a',
            borderColor: '#25633b',
            borderWidth: 1.5
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
            padding: 10
        },
        plugins: {
            legend: commonLegend
        },
        scales: {
            x: {
                ticks: {
                    color: commonTickColor
                },
                grid: {
                    color: commonGridColor
                }
            },
            y: {
                min: 0,
                max: 100,
                ticks: {
                    color: commonTickColor
                },
                grid: {
                    color: commonGridColor
                }
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
            backgroundColor: '#102a43',
            borderColor: '#0b2034',
            borderWidth: 1.5
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
            padding: 10
        },
        plugins: {
            legend: commonLegend
        },
        scales: {
            x: {
                ticks: {
                    color: commonTickColor
                },
                grid: {
                    color: commonGridColor
                }
            },
            y: {
                beginAtZero: true,
                ticks: {
                    color: commonTickColor
                },
                grid: {
                    color: commonGridColor
                }
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
    <div class="hero-title">Saved observation records</div>
    <p class="hero-copy mb-0">
        Review exactly what was stored for each session before presenting or discussing the dashboard.
    </p>
</div>

<div class="content-panel">
    <div class="records-note mb-3">All saved sessions are shown newest first.</div>
    <div class="table-shell">
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
        'CEC 320 Entry',
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
        'avg_engagement': round(sum(engagement) / len(engagement), 1) if engagement else 0,
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
