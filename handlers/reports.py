import os
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta

from database import (
    get_all_kpi, delete_kpi_record, update_kpi_score,
    get_branch_kpi_summary
)
from config import ADMIN_IDS
from keyboards import boss_menu, get_kpi_boss_inline_kb
from states import EditKPIForm

router = Router()

@router.message(F.text == "📊 Haftalik hisobot")
async def show_weekly_report_admin(message: Message):
    tg_id = message.from_user.id
    if tg_id not in ADMIN_IDS:
        return
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    text = f"🏢 **Filiallar kesimida haftalik hisobot** ({start_date} — {end_date}):\n\n"
    for branch in ["Diamond-1", "Diamond-2", "Diamond-3"]:
        text += f"🔹 **{branch}:**\n"
        summary = get_branch_kpi_summary(branch, start_date, end_date)
        if not summary:
            text += "   Ma'lumotlar yo'q\n\n"
        else:
            for s in summary:
                text += f"   - {s[0]}: ⭐️ {s[1]} ball ({s[2]} ta vazifa)\n"
            text += "\n"
    await message.answer(text)

@router.message(F.text == "📊 KPI hisobotlarini ko'rish")
async def show_boss_kpi_reports(message: Message):
    kpis = get_all_kpi()
    if not kpis:
        await message.answer("📭 Hozircha KPI natijalari yo'q.")
        return
        
    for item in kpis[:10]:
        text = (
            f"👤 **{item[1]}** ({item[2]})\n"
            f"📅 Sana: {item[3]} | 💼 Vazifa: {item[4]}\n"
            f"💰 Summa: {item[6]} so'm | ⭐️ Ball: {item[7]}"
        )
        if item[5]:
            try:
                if "ochilish" in item[4].lower():
                    await message.answer_video_note(item[5], caption=text, reply_markup=get_kpi_boss_inline_kb(item[0]))
                else:
                    await message.answer_photo(item[5], caption=text, reply_markup=get_kpi_boss_inline_kb(item[0]))
            except Exception:
                await message.answer(text, reply_markup=get_kpi_boss_inline_kb(item[0]))
        else:
            await message.answer(text, reply_markup=get_kpi_boss_inline_kb(item[0]))

@router.message(F.text == "📥 Excel hisobot")
async def get_excel_report_handler(message: Message):
    tg_id = message.from_user.id
    if tg_id not in ADMIN_IDS:
        await message.answer("⚠️ Bu buyruq faqat rahbarlar uchun!")
        return
        
    # Excel faylini generatsiya qilish funksiyasi agar reports.py da bo'lmasa, uni database yoki boshqa joydan chaqirish mumkin
    try:
        from reports_excel import generate_excel_report # Agar alohida faylda bo'lsa
    except ImportError:
        pass
    
    file_path = generate_excel_report() if 'generate_excel_report' in globals() else None
    if file_path and os.path.exists(file_path):
        await message.answer_document(FSInputFile(file_path), caption="📊 Barcha KPI natijalari Excel hisoboti")
    else:
        await message.answer("📭 Hozircha eksport qilish uchun ma'lumotlar yo'q.")

@router.callback_query(F.data.startswith("del_kpi_"))
async def delete_kpi_cb(call: CallbackQuery):
    kpi_id = int(call.data.split("_")[2])
    delete_kpi_record(kpi_id)
    await call.message.edit_text("❌ KPI hisoboti o'chirildi! Endi xodim buni qaytadan kiritishi mumkin.")
    await call.answer()

@router.callback_query(F.data.startswith("edit_kpi_"))
async def edit_kpi_cb(call: CallbackQuery, state: FSMContext):
    kpi_id = int(call.data.split("_")[2])
    await state.update_data(editing_kpi_id=kpi_id)
    await state.set_state(EditKPIForm.new_score)
    await call.message.answer("✏️ Ushbu KPI uchun yangi ball miqdorini raqamda kiriting:")
    await call.answer()

@router.message(EditKPIForm.new_score)
async def save_edited_score(message: Message, state: FSMContext):
    try:
        new_score = int(message.text)
    except ValueError:
        await message.answer("⚠️ Iltimos, faqat butun son ko'rinishida ball kiriting:")
        return
        
    data = await state.get_data()
    kpi_id = data.get("editing_kpi_id")
    
    update_kpi_score(kpi_id, new_score)
    await message.answer("✅ KPI balli muvaffaqiyatli yangilandi!", reply_markup=boss_menu)
    await state.clear()