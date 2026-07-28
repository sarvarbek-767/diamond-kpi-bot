import asyncio
import logging
import os
import sys
from datetime import datetime
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from database import init_db, get_connection, get_employees
from config import API_TOKEN, ADMIN_IDS

# Modullarga bo'lingan routerlarni import qilish
from handlers import (
    start_router,
    employee_router,
    kpi_router,
    reports_router,
    admin_router,
    callbacks_router,
    reminders_router
)

async def send_scheduled_reminders_and_reports(bot: Bot):
    last_day_reported = None
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
    
    while True:
        now = datetime.now()
        current_time_str = now.strftime("%H:%M")
        current_date_str = now.strftime("%Y-%m-%d")

        # Kunlik eslatmalar (10:00, 15:00, 21:00)
        if current_time_str in ["10:00", "15:00", "21:00"]:
            emps = get_employees()
            for emp in emps:
                tg_id = emp[4]
                if tg_id:
                    with get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT task_name FROM kpi_records WHERE telegram_id = ? AND date = ?", (tg_id, current_date_str))
                        done_tasks = [row[0] for row in cursor.fetchall()]
                    
                    missing_tasks = [t for t in all_tasks if t not in done_tasks]
                    
                    text = f"⏰ **Eslatma!** Bugungi sana: {current_date_str}\n\n"
                    if missing_tasks:
                        text += "Siz hali quyidagi vazifalar bo'yicha KPI kiritmadingiz:\n"
                        for mt in missing_tasks:
                            text += f"• {mt}\n"
                        text += "\nIltimos, o'z vaqtida kiriting! 📊"
                    else:
                        text += "Siz bugungi barcha vazifalarni bajargansiz! Barakalla! 🎉"
                        
                    try:
                        await bot.send_message(tg_id, text)
                    except Exception:
                        pass
            await asyncio.sleep(60)

        # Kunlik yakuniy hisobot (Har kuni kechqurun 22:00 da rahbarlarga filiallar kesimida)
        if current_time_str == "22:00" and last_day_reported != current_date_str:
            last_day_reported = current_date_str
            emps = get_employees()
            
            for admin_id in ADMIN_IDS:
                try:
                    report_text = f"📊 **Kunlik yakuniy KPI hisoboti ({current_date_str})**\n\n"
                    for branch in ["Diamond-1", "Diamond-2", "Diamond-3"]:
                        report_text += f"🏢 **Filial: {branch}**\n"
                        branch_emps = [e for e in emps if e[2] == branch]
                        
                        if not branch_emps:
                            report_text += "   Xodimlar mavjud emas.\n\n"
                            continue

                        for emp in branch_emps:
                            tg_id = emp[4]
                            emp_name = emp[1]
                            with get_connection() as conn:
                                cursor = conn.cursor()
                                cursor.execute("SELECT task_name, score FROM kpi_records WHERE telegram_id = ? AND date = ?", (tg_id, current_date_str))
                                records = cursor.fetchall()
                            done_dict = {r[0]: r[1] for r in records}
                            
                            report_text += f"   👤 {emp_name}:\n"
                            for t in all_tasks:
                                if t in done_dict:
                                    report_text += f"    ✅ {t} (+{done_dict[t]} ball)\n"
                                else:
                                    report_text += f"    ❌ {t} (Bajarilmadi)\n"
                            report_text += "\n"
                            
                    await bot.send_message(admin_id, report_text)
                except Exception:
                    pass

        await asyncio.sleep(30)


# Render port talabini qondirish uchun veb-server
async def handle(request):
    return web.Response(text="Bot is live!")[cite: 1]


async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)[cite: 1]
    init_db()[cite: 1]

    bot = Bot(token=API_TOKEN)[cite: 1]
    dp = Dispatcher()[cite: 1]
    
    # Barcha modullardagi routerlarni Dispatcherga to'g'ri ulash
    dp.include_router(start_router)[cite: 1]
    dp.include_router(employee_router)[cite: 1]
    dp.include_router(kpi_router)[cite: 1]
    dp.include_router(reports_router)[cite: 1]
    dp.include_router(admin_router)[cite: 1]
    dp.include_router(callbacks_router)[cite: 1]
    dp.include_router(reminders_router)[cite: 1]

    await bot.set_my_commands(
        [BotCommand(command="start", description="Botni ishga tushirish")][cite: 1]
    )

    # Rejalashtirilgan xabarlarni fon rejimida ishga tushirish
    asyncio.create_task(send_scheduled_reminders_and_reports(bot))[cite: 1]

    # --- Render uchun Web Server (Portni ushlab turish) ---
    port = int(os.environ.get("PORT", 8080))[cite: 1]
    app = web.Application()[cite: 1]
    app.router.add_get("/", handle)[cite: 1]

    runner = web.AppRunner(app)[cite: 1]
    await runner.setup()[cite: 1]
    site = web.TCPSite(runner, "0.0.0.0", port)[cite: 1]
    await site.start()[cite: 1]
    # -----------------------------------------------------

    print("Bot muvaffaqiyatli ishga tushdi...")[cite: 1]
    await dp.start_polling(bot)[cite: 1]


if __name__ == "__main__":
    asyncio.run(main())[cite: 1]