from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = "engagement.db"

STUDENTS = [
    "John Cena"
]

BASE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            background: linear-gradient(135deg, #0f172a, #111827 55%, #1e293b);
            min-height: 100vh;
            color: #e5e7eb;
        }
        .glass {
            background: rgba(255,255,255,0.08);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255,255,255,0.12);
            box-shadow: 0 20px 60px rgba(0,0,0,0.35);
            border-radius: 24px;
        }
        .hero-title {
            font-weight: 800;
            letter-spacing: -0.03em;
        }
        .subtle {
            color: #cbd5e1;
        }
        .table-dark-custom {
            --bs-table-bg: transparent;
            --bs-table-color: #f8fafc;
            --bs-table-border-color: rgba(255,255,255,0.08);
            vertical-align: middle;
        }
        .student-cell {
            font-weight: 600;
            min-width: 180px;
        }
        .form-check-input {
            transform: scale(1.2);
        }
        .pill {
            display: inline-block;
            padding: 0.35rem 0.75rem;
            border-radius: 999px;
            background: rgba(59,130,246,0.18);
            color: #bfdbfe;
            font-size: 0.85rem;
            border: 1px solid rgba(96,165,250,0.25);
        }
        .metric-card {
            border-radius: 20px;
            padding: 1rem 1.25rem;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.08);
        }
        .metric-number {
            font-size: 1.8rem;
            font-weight: 800;
        }
        .sticky-actions {
            position: sticky;
            bottom: 16px;
            z-index: 50;
        }
        input[type='number'] {
            min-width: 82px;
        }
        .notes-input {
            min-width: 180px;
        }
        canvas {
            background: rgba(255,255,255,0.03);
            border-radius: 18px;
            padding: 10px;
        }
        .navbar-brand {
            font-weight: 800;
            letter-spacing: -0.03em;
        }
    </style>
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-transparent py-3">
    <div class="container">
        <a class="navbar-brand" href="/">Engagement Tracker</a>
        <div class="d-flex gap-2">
            <a href="/" class="btn btn-outline-light btn-sm">Entry</a>
            <a href="/dashboard" class="btn btn-primary btn-sm">Dashboard</a>
            <a href="/records" class="btn btn-outline-info btn-sm">Records</a>
        </div>
    </div>
</nav>

<div class="container py-4 py-md-5">
    {{ content|safe }}
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

INDEX_HTML = """
<div class="glass p-4 p-md-5 mb-4">
    <div class="d-flex flex-column flex-lg-row justify-content-between align-items-lg-end gap-3 mb-4">
        <div>
            <div class="pill mb-3">Fast classroom data entry</div>
            <h1 class="hero-title display-5 mb-2">Track engagement with a cleaner UI</h1>
            <p class="subtle mb-0">Enter attendance, engagement, participation, and notes for each student. Save one class session at a time.</p>
        </div>
        <div class="metric-card text-center">
            <div class="subtle small">Students loaded</div>
            <div class="metric-number">{{ students|length }}</div>
        </div>
    </div>

    <form method="POST">
        <div class="row g-3 align-items-end mb-4">
            <div class="col-md-4">
                <label class="form-label">Session Date</label>
                <input type="date" class="form-control form-control-lg" name="session_date" value="{{ today }}" required>
            </div>
            <div class="col-md-8">
                <div class="metric-card h-100 d-flex flex-column justify-content-center">
                    <div class="fw-semibold mb-1">How to use this page</div>
                    <div class="subtle">Engagement = attentive / following along. Participation = active speaking or peer interaction. Use notes for quick context.</div>
                </div>
            </div>
        </div>

        <div class="table-responsive glass p-3">
            <table class="table table-dark-custom align-middle mb-0">
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
                        <td><input class="form-control form-control-sm notes-input" type="text" name="notes_{{ student['id'] }}" placeholder="Optional note"></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="sticky-actions mt-4 d-flex justify-content-end gap-2">
            <a href="/dashboard" class="btn btn-outline-info btn-lg">View Graphs</a>
            <button type="submit" class="btn btn-success btn-lg px-4">Save Session</button>
        </div>
    </form>
</div>
"""

DASHBOARD_HTML = """
<div class="glass p-4 p-md-5 mb-4">
    <div class="d-flex flex-column flex-lg-row justify-content-between align-items-lg-end gap-3 mb-4">
        <div>
            <div class="pill mb-3">Automatic graph maker</div>
            <h1 class="hero-title display-5 mb-2">Session analytics dashboard</h1>
            <p class="subtle mb-0">Plots attendance, participation, engagement, and question activity directly from the database.</p>
        </div>
        <div class="d-flex gap-3 flex-wrap">
            <div class="metric-card text-center">
                <div class="subtle small">Sessions</div>
                <div class="metric-number">{{ summary.sessions }}</div>
            </div>
            <div class="metric-card text-center">
                <div class="subtle small">Avg Attendance</div>
                <div class="metric-number">{{ summary.avg_attendance }}%</div>
            </div>
            <div class="metric-card text-center">
                <div class="subtle small">Avg Participation</div>
                <div class="metric-number">{{ summary.avg_participation }}%</div>
            </div>
        </div>
    </div>

    {% if labels %}
    <div class="row g-4">
        <div class="col-12">
            <div class="glass p-3">
                <h4 class="mb-3">Attendance vs Participation</h4>
                <canvas id="lineChart" height="120"></canvas>
            </div>
        </div>
        <div class="col-lg-6">
            <div class="glass p-3">
                <h4 class="mb-3">Average Engagement Score</h4>
                <canvas id="engagementChart" height="150"></canvas>
            </div>
        </div>
        <div class="col-lg-6">
            <div class="glass p-3">
                <h4 class="mb-3">Questions / Comments</h4>
                <canvas id="questionsChart" height="150"></canvas>
            </div>
        </div>
    </div>
    {% else %}
    <div class="alert alert-info">No session data yet. Go to the entry page and save a class session first.</div>
    {% endif %}
</div>

{% if labels %}
<script>
const labels = {{ labels|safe }};
const attendance = {{ attendance|safe }};
const participation = {{ participation|safe }};
const engagement = {{ engagement|safe }};
const questions = {{ questions|safe }};

new Chart(document.getElementById('lineChart'), {
    type: 'line',
    data: {
        labels,
        datasets: [
            {
                label: 'Attendance %',
                data: attendance,
                tension: 0.25,
                borderWidth: 3,
                fill: false
            },
            {
                label: 'Participation %',
                data: participation,
                tension: 0.25,
                borderWidth: 3,
                fill: false
            }
        ]
    },
    options: {
        responsive: true,
        plugins: { legend: { labels: { color: '#e5e7eb' } } },
        scales: {
            x: { ticks: { color: '#cbd5e1' }, grid: { color: 'rgba(255,255,255,0.08)' } },
            y: {
                min: 0,
                max: 100,
                ticks: { color: '#cbd5e1' },
                grid: { color: 'rgba(255,255,255,0.08)' }
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
            borderWidth: 1
        }]
    },
    options: {
        plugins: { legend: { labels: { color: '#e5e7eb' } } },
        scales: {
            x: { ticks: { color: '#cbd5e1' }, grid: { color: 'rgba(255,255,255,0.08)' } },
            y: {
                min: 0,
                max: 100,
                ticks: { color: '#cbd5e1' },
                grid: { color: 'rgba(255,255,255,0.08)' }
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
            borderWidth: 1
        }]
    },
    options: {
        plugins: { legend: { labels: { color: '#e5e7eb' } } },
        scales: {
            x: { ticks: { color: '#cbd5e1' }, grid: { color: 'rgba(255,255,255,0.08)' } },
            y: {
                beginAtZero: true,
                ticks: { color: '#cbd5e1' },
                grid: { color: 'rgba(255,255,255,0.08)' }
            }
        }
    }
});
</script>
{% endif %}
"""

RECORDS_HTML = """
<div class="glass p-4 p-md-5">
    <div class="d-flex justify-content-between align-items-end mb-4 gap-3 flex-wrap">
        <div>
            <div class="pill mb-3">All saved entries</div>
            <h1 class="hero-title display-6 mb-2">Observation records</h1>
            <p class="subtle mb-0">Use this page to verify what was stored in the database.</p>
        </div>
    </div>

    <div class="table-responsive glass p-3">
        <table class="table table-dark-custom align-middle mb-0">
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
                    <td>{{ row['full_name'] }}</td>
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
    return render_template_string(BASE_HTML, title=title, content=render_template_string(content, **context))


@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        session_date = request.form['session_date']
        cur.execute("INSERT OR IGNORE INTO class_sessions (session_date) VALUES (?)", (session_date,))
        conn.commit()

        session_row = cur.execute("SELECT id FROM class_sessions WHERE session_date = ?", (session_date,)).fetchone()
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
                    student_id, session_id, engaged_first_half, engaged_second_half,
                    participated, questions_comments, absent, notes
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
        labels=labels,
        attendance=attendance,
        participation=participation,
        engagement=engagement,
        questions=questions,
        summary=summary
    )


if __name__ == '__main__':
    init_db()
    seed_students()
    app.run(host="0.0.0.0", port= 5000, debug=False)
