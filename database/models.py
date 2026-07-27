def create_tables(conn):
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        branch TEXT NOT NULL,
        position TEXT NOT NULL,
        telegram_id INTEGER UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kpi_records(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        full_name TEXT,
        branch TEXT,
        date TEXT,
        task_name TEXT,
        media_file_id TEXT,
        amount REAL DEFAULT 0,
        score INTEGER DEFAULT 0
    )
    """)