import asyncio
import logging
import os
from datetime import datetime
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from handlers import router
from database import get_employees, conn
from config import API_TOKEN

async def send_reminder(bot: Bot):
    employees = get_employees() 
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id, task_name FROM kpi_records WHERE date = ?", (current_date,))
    today_records = cursor.fetchall()
    
    emp_tasks = {}
    for tg_id, task_name in today_records:
        if tg_id not in emp_tasks:
            emp_tasks[tg_id] = []
        emp_tasks[tg_id].append(task_name)
        
    all_tasks = [
        "📹 Har kuni ochilish videosi",
        "🧹 Tozalik va tartib (10 ball)",
        "📱 Instagram post",
        "📸 Instagram stories",
        "👀 3000+ ko'rish",
        "💰 Savdo rejasi",
        "📉 Qarzdorlik oshmasligi",
        "🎁 Bonus me'yoridan oshmasligi"
    ]
    
    for emp in employees:
        tg_id = emp[4]
        if not tg_id or tg_id == 0:
            continue
            
        completed = emp_tasks.get(tg_id, [])
        missing_tasks = [t for t in all_tasks if t not in completed]
        
        if missing_tasks:
            text = (
                f"⏰ **Eslatma!** Bugungi sana: {current_date}\n\n"
                f"Siz hali quyidagi vazifalar bo'yicha KPI kiritmadingiz:\n"
            )
            for task in missing_tasks:
                text += f"• {task}\n"
                
            text += "\nIltimos, o'z vaqtida KPI ma'lumotlarini kiriting! 📊"
            
            try:
                await bot.send_message(chat_id=tg_id, text=text)
            except Exception as e:
                logging.error(f"Xabar yuborishda xatolik (TG ID: {tg_id}): {e}")

async def main():
    if not os.path.exists("data"):
        os.makedirs("data")
        
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    
    dp.include_router(router)
    
    scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")
    scheduler.add_job(send_reminder, "cron", hour="10,15,21", minute=0, args=[bot])
    scheduler.start()
    
    print("🚀 DIAMOND KPI BOT va Eslatmalar tizimi muvaffaqiyatli ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())