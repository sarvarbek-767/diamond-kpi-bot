import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from database.database import get_connection

logger = logging.getLogger(__name__)

async def send_daily_reminder(bot: Bot):
    """
    Har kuni soat 20:00 da xodimlarga KPI kiritishlarini eslatib turuvchi funksiya.
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # Barcha xodimlarning telegram_id larini olamiz
            cursor.execute("SELECT telegram_id FROM employees")
            employees = cursor.fetchall()
            
        for emp in employees:
            telegram_id = emp[0]
            try:
                await bot.send_message(
                    chat_id=telegram_id,
                    text="🔔 **Eslatma:** Bugungi KPI natijalaringizni kiritish esdan chiqmasin! 📊\n\n"
                         "Iltimos, botga kirib bugungi vazifalaringizni yuboring."
                )
            except Exception as e:
                logger.error(f"Xodimga eslatma yuborishda xatolik ({telegram_id}): {e}")
                
    except Exception as e:
        logger.error(f"Kunlik eslatma funksiyasida xatolik: {e}")

def setup_scheduler(bot: Bot):
    """
    Scheduler ni sozlash va ishga tushirish.
    """
    scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")
    
    # Masalan: Har kuni kechki soat 20:00 da eslatma yuborish
    scheduler.add_job(send_daily_reminder, 'cron', hour=20, minute=0, args=[bot])
    
    scheduler.start()
    logger.info("Scheduler muvaffaqiyatli ishga tushirildi! ⏰")