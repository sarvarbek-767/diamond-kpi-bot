from pathlib import Path
from contextlib import contextmanager
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "kpi.db"


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode=WAL")

    try:
        yield conn
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT,
                branch TEXT,
                position TEXT,
                telegram_id INTEGER UNIQUE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kpi_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                branch TEXT,
                task_name TEXT,
                score INTEGER,
                amount REAL,
                date TEXT
            )
        """)
        conn.commit()


def get_employee_by_tg_id(telegram_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE telegram_id = ?", (telegram_id,))
        return cursor.fetchone()


def delete_kpi_record(record_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM kpi_records WHERE id = ?", (record_id,))
        conn.commit()


def get_employees():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees")
        return cursor.fetchall()


def get_all_kpi():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM kpi_records")
        return cursor.fetchall()


def update_kpi_score(record_id, new_score):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE kpi_records SET score = ? WHERE id = ?", (new_score, record_id))
        conn.commit()


def get_branch_kpi_summary():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT branch, SUM(score) FROM kpi_records GROUP BY branch")
        return cursor.fetchall()
def add_employee(full_name, branch, position, telegram_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO employees (full_name, branch, position, telegram_id) VALUES (?, ?, ?, ?)",
            (full_name, branch, position, telegram_id)
        )
        conn.commit()
def delete_employee(employee_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
        conn.commit()
def get_kpi_by_telegram_id(telegram_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM kpi_records WHERE telegram_id = ?", (telegram_id,))
        return cursor.fetchall()
def get_weekly_kpi_by_employee(telegram_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM kpi_records WHERE telegram_id = ? AND date >= date('now', '-7 days')", (telegram_id,))
        return cursor.fetchall()
def add_employee(full_name, branch, position, telegram_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO employees (full_name, branch, position, telegram_id) VALUES (?, ?, ?, ?)",
            (full_name, branch, position, telegram_id)
        )
        conn.commit()

def delete_employee(employee_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
        conn.commit()

def get_kpi_by_telegram_id(telegram_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM kpi_records WHERE telegram_id = ?", (telegram_id,))
        return cursor.fetchall()

def get_weekly_kpi_by_employee(telegram_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM kpi_records WHERE telegram_id = ? AND date >= date('now', '-7 days')", (telegram_id,))
        return cursor.fetchall()
def save_kpi_record(telegram_id, full_name, branch, date, task_name, media_file_id, amount, score):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO kpi_records (telegram_id, full_name, branch, date, task_name, media_file_id, amount, score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (telegram_id, full_name, branch, date, task_name, media_file_id, amount, score)
        )
        conn.commit()

def check_task_exists(telegram_id, date, task_name):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM kpi_records WHERE telegram_id = ? AND date = ? AND task_name = ?",
            (telegram_id, date, task_name)
        )
        return cursor.fetchone() is not None