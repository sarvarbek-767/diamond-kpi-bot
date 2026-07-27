from datetime import datetime
from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database import (
    save_kpi_record, get_employee_by_tg_id, check_task_exists
)
from config import ADMIN_IDS
from bonus import get_task_details, calculate_proportional_score
from keyboards import employee_main_menu, kpi_tasks_menu
from states import KPIForm

router = Router()

@router.message(F.text == "📊 KPI kiritish")
async def start_kpi(message: Message, state: FSMContext):
    await state.set_state(KPIForm.task_name)
    await message.answer("📋 Bajarilgan vazifani tanlang:", reply_markup=kpi_tasks_menu)

@router.message(KPIForm.task_name)
async def process_kpi_task(message: Message, state: FSMContext):
    task_name = message.text
    max_score, input_type, target_plan = get_task_details(task_name)

    if input_type == "none":
        await message.answer("⚠️ Iltimos, ro'yxatdagi vazifalardan birini tugma orqali tanlang!")
        return

    current_date = datetime.now().strftime("%Y-%m-%d")
    tg_id = message.from_user.id

    if check_task_exists(tg_id, current_date, task_name):
        await message.answer(
            "⚠️ Siz bugun ushbu vazifa bo'yicha ma'lumot kiritgansiz.\n"
            "Agar o'zgartirmoqchi bo'lsangiz, avval rahbar bu natijani o'chirishi kerak."
        )
        await state.clear()
        return

    await state.update_data(task_name=task_name, base_score=max_score, input_type=input_type)
    
    if input_type == "media":
        await state.set_state(KPIForm.media)
        if "ochilish" in task_name.lower() or "tozalik" in task_name.lower():
            await message.answer(
                "⭕️ Iltimos, ushbu vazifa uchun faqat **Dumaloq video (video note)** yuboring:",
                reply_markup=employee_main_menu
            )
        else:
            await message.answer(
                "📸 Iltimos, ushbu vazifa uchun **Skrinshot yoki Rasm** yuboring:",
                reply_markup=employee_main_menu
            )
    elif input_type == "amount":
        await state.set_state(KPIForm.amount)
        await message.answer(
            "💰 Iltimos, tegishli summani **faqat so'mda** raqam bilan kiriting (masalan: 15000000):",
            reply_markup=employee_main_menu
        )

@router.message(KPIForm.media, F.video_note)
async def process_kpi_video_note(message: Message, state: FSMContext):
    await save_record_to_db(message, state, media_file_id=message.video_note.file_id, amount=0.0)

@router.message(KPIForm.media, F.photo)
async def process_kpi_photo(message: Message, state: FSMContext):
    await save_record_to_db(message, state, media_file_id=message.photo[-1].file_id, amount=0.0)

@router.message(KPIForm.media)
async def process_kpi_wrong_media(message: Message):
    await message.answer("⚠️ Iltimos, talab qilingan formatda rasm yoki dumaloq video yuboring!")

@router.message(KPIForm.amount)
async def process_kpi_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(" ", "").replace(",", ""))
    except ValueError:
        await message.answer("⚠️ Faqat raqam ko'rinishida summa kiriting (masalan: 15000000):")
        return
    
    data = await state.get_data()
    proportional_score = calculate_proportional_score(data["task_name"], amount)
    await state.update_data(calculated_score=proportional_score)
    
    await save_record_to_db(message, state, media_file_id=None, amount=amount)

async def save_record_to_db(message: Message, state: FSMContext, media_file_id, amount):
    data = await state.get_data()
    tg_id = message.from_user.id
    
    emp = get_employee_by_tg_id(tg_id)
    if emp:
        full_name = emp[1]
        branch = emp[2]
    else:
        full_name = message.from_user.full_name
        branch = "Diamond-1"

    current_date = datetime.now().strftime("%Y-%m-%d")
    score = data.get("calculated_score") if "calculated_score" in data else data.get("base_score", 0)
    
    save_kpi_record(
        telegram_id=tg_id,
        full_name=full_name,
        branch=branch,
        date=current_date,
        task_name=data["task_name"],
        media_file_id=media_file_id,
        amount=amount,
        score=score
    )
    
    for admin_id in ADMIN_IDS:
        try:
            caption_text = (
                f"🔔 **Yangi KPI kiritildi!**\n\n"
                f"👤 Xodim: {full_name}\n"
                f"🏢 Filial: {branch}\n"
                f"💼 Vazifa: {data['task_name']}\n"
                f"⭐️ Ball: {score}"
            )
            if media_file_id:
                if "video" in data['task_name'].lower() or "ochilish" in data['task_name'].lower():
                    await message.bot.send_video_note(admin_id, media_file_id)
                    await message.bot.send_message(admin_id, caption_text)
                else:
                    await message.bot.send_photo(admin_id, media_file_id, caption=caption_text)
            else:
                await message.bot.send_message(admin_id, caption_text)
        except Exception:
            pass

    await message.answer(
        f"✅ **KPI muvaffaqiyatli saqlandi!**\n\n"
        f"👤 Xodim: {full_name}\n"
        f"🏢 Filial: {branch}\n"
        f"📅 Sana: {current_date}\n"
        f"💼 Vazifa: {data['task_name']}\n"
        f"⭐️ Hisoblangan ball: {score}",
        reply_markup=employee_main_menu
    )
    await state.clear()