from .database import (
    get_connection,
    get_employees,
    get_employee_by_tg_id,
    get_all_kpi,
    delete_kpi_record,
    update_kpi_score,
    get_branch_kpi_summary,
    add_employee,
    delete_employee,
    get_kpi_by_telegram_id,
    get_weekly_kpi_by_employee,
    save_kpi_record,
    check_task_exists
)

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