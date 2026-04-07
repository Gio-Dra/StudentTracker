from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_NAME = "engagement.db"


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
        session_date DATE NOT NULL UNIQUE
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
    names = [
        "Alex Carter", "Jordan Lee", "Taylor Morgan", "Casey Nguyen",
        "Riley Bennett", "Cameron Diaz", "Avery Brooks", "Morgan Patel",
        "Dylan Rivera", "Skyler Adams", "Quinn Foster", "Parker Kim",
        "Reese Turner", "Hayden Scott", "Logan Cruz", "Jamie Flores",
        "Blake Simmons", "Dakota Reed", "Emerson Clark"
    ]

    conn = get_db_connection()
    cur = conn.cursor()

    for name in names:
        cur.execute("INSERT OR IGNORE INTO students (full_name) VALUES (?)", (name,))

    conn.commit()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        session_date = request.form["session_date"]

        cur.execute("INSERT OR IGNORE INTO class_sessions (session_date) VALUES (?)", (session_date,))
        conn.commit()

        cur.execute("SELECT id FROM class_sessions WHERE session_date = ?", (session_date,))
        session_id = cur.fetchone()["id"]

        students = cur.execute("SELECT * FROM students ORDER BY full_name").fetchall()

        for student in students:
            sid = student["id"]

            engaged_first = 1 if request.form.get(f"engaged_first_{sid}") else 0
            engaged_second = 1 if request.form.get(f"engaged_second_{sid}") else 0
            participated = 1 if request.form.get(f"participated_{sid}") else 0
            absent = 1 if request.form.get(f"absent_{sid}") else 0

            questions_comments = request.form.get(f"questions_{sid}", "0")
            notes = request.form.get(f"notes_{sid}", "")

            cur.execute("""
                INSERT INTO observations
                (student_id, session_id, engaged_first_half, engaged_second_half, participated,
                 questions_comments, absent, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(student_id, session_id) DO UPDATE SET
                    engaged_first_half=excluded.engaged_first_half,
                    engaged_second_half=excluded.engaged_second_half,
                    participated=excluded.participated,
                    questions_comments=excluded.questions_comments,
                    absent=excluded.absent,
                    notes=excluded.notes
            """, (
                sid, session_id, engaged_first, engaged_second,
                participated, int(questions_comments), absent, notes
            ))

        conn.commit()
        conn.close()
        return redirect(url_for("report"))

    students = cur.execute("SELECT * FROM students ORDER BY full_name").fetchall()
    conn.close()
    return render_template("index.html", students=students)


@app.route("/report")
def report():
    conn = get_db_connection()
    cur = conn.cursor()

    rows = cur.execute("""
        SELECT
            s.full_name,
            cs.session_date,
            o.engaged_first_half,
            o.engaged_second_half,
            o.participated,
            o.questions_comments,
            o.absent,
            o.notes
        FROM observations o
        JOIN students s ON o.student_id = s.id
        JOIN class_sessions cs ON o.session_id = cs.id
        ORDER BY cs.session_date DESC, s.full_name ASC
    """).fetchall()

    conn.close()
    return render_template("report.html", rows=rows)


if __name__ == "__main__":
    init_db()
    seed_students()
    app.run(debug=True)