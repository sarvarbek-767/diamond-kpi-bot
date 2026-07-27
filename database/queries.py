from .database import get_connection


def add_employee(full_name, branch, position, telegram_id):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO employees
            (full_name, branch, position, telegram_id)
            VALUES (?, ?, ?, ?)
            """,
            (full_name, branch, position, telegram_id),
        )


def get_employees():
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT
                id,
                full_name,
                branch,
                position,
                telegram_id
            FROM employees
            ORDER BY full_name
            """
        ).fetchall()


def get_employee_by_tg_id(tg_id):
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT
                id,
                full_name,
                branch,
                position,
                telegram_id
            FROM employees
            WHERE telegram_id=?
            """,
            (tg_id,),
        ).fetchone()


def delete_employee(emp_id):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM employees WHERE id=?",
            (emp_id,),
        )
        from .database import get_connection


# ================= KPI CRUD =================

def save_kpi_record(
    telegram_id,
    full_name,
    branch,
    date,
    task_name,
    media_file_id,
    amount,
    score
):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO kpi_records(
                telegram_id,
                full_name,
                branch,
                date,
                task_name,
                media_file_id,
                amount,
                score
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                telegram_id,
                full_name,
                branch,
                date,
                task_name,
                media_file_id,
                amount,
                score,
            ),
        )


def get_all_kpi():
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT
                id,
                full_name,
                branch,
                date,
                task_name,
                media_file_id,
                amount,
                score
            FROM kpi_records
            ORDER BY id DESC
            """
        ).fetchall()


def get_kpi_by_branch(branch):
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT
                id,
                full_name,
                branch,
                date,
                task_name,
                media_file_id,
                amount,
                score
            FROM kpi_records
            WHERE branch=?
            ORDER BY id DESC
            """,
            (branch,),
        ).fetchall()


def get_kpi_by_telegram_id(telegram_id):
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT
                id,
                full_name,
                branch,
                date,
                task_name,
                media_file_id,
                amount,
                score
            FROM kpi_records
            WHERE telegram_id=?
            ORDER BY id DESC
            """,
            (telegram_id,),
        ).fetchall()


def delete_kpi_record(kpi_id):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM kpi_records WHERE id=?",
            (kpi_id,),
        )


def update_kpi_score(kpi_id, new_score):
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE kpi_records
            SET score=?
            WHERE id=?
            """,
            (new_score, kpi_id),
        )


def check_task_exists(
    telegram_id: int,
    date: str,
    task_name: str,
):
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id
            FROM kpi_records
            WHERE telegram_id=?
              AND date=?
              AND task_name=?
            """,
            (
                telegram_id,
                date,
                task_name,
            ),
        ).fetchone()

    return row is not None


def get_total_score_by_branch(branch):
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT SUM(score)
            FROM kpi_records
            WHERE branch=?
            """,
            (branch,),
        ).fetchone()

    return row[0] if row[0] else 0


# ================= HISOBOT =================

def get_weekly_kpi_by_employee(
    telegram_id,
    start_date,
    end_date,
):
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT
                task_name,
                SUM(amount),
                SUM(score),
                COUNT(id)
            FROM kpi_records
            WHERE telegram_id=?
              AND date BETWEEN ? AND ?
            GROUP BY task_name
            """,
            (
                telegram_id,
                start_date,
                end_date,
            ),
        ).fetchall()


def get_branch_kpi_summary(
    branch,
    start_date,
    end_date,
):
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT
                full_name,
                SUM(score),
                COUNT(id)
            FROM kpi_records
            WHERE branch=?
              AND date BETWEEN ? AND ?
            GROUP BY telegram_id
            """,
            (
                branch,
                start_date,
                end_date,
            ),
        ).fetchall()