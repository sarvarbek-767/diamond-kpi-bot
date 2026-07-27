import pandas as pd
import sqlite3
import os

def generate_excel_report(branch=None):
    conn = sqlite3.connect("data/kpi.db")
    if branch:
        query = "SELECT id, full_name, branch, date, task_name, amount, score FROM kpi_records WHERE branch = ? ORDER BY id DESC"
        df = pd.read_sql(query, conn, params=(branch,))
    else:
        query = "SELECT id, full_name, branch, date, task_name, amount, score FROM kpi_records ORDER BY id DESC"
        df = pd.read_sql(query, conn)
    conn.close()
    
    df.columns = ["ID", "F.I.Sh", "Filial", "Sana", "Vazifa", "Summa (so'm)", "Ball"]
    
    if not os.path.exists("reports"):
        os.makedirs("reports")
        
    filename = f"reports/KPI_Hisobot_{branch}.xlsx" if branch else "reports/KPI_Hisobot_Barcha.xlsx"
    df.to_excel(filename, index=False, engine='openpyxl')
    return filename