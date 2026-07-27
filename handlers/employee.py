from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Router

router = Router()

# Qolgan kodlaringiz shu yerda yozilgan bo'lishi kerak...

from database import (
    add_employee, get_employees, delete_employee, 
    get_employee_by_tg_id, get_kpi_by_telegram_id,
    get_weekly_kpi_by_employee
)
from keyboards import (
    employee_menu, branch_select_menu, employee_main_menu, 
    get_employee_inline_kb
)
from states import EmployeeForm
from datetime import datetime, timedelta

router = Router()

@router.message(F.text == "👥 Xodimlar")
async def show_employee_menu(message: Message):
    await message.answer("👥 Xodimlarni boshqarish bo'limi:", reply_markup=employee_menu)

@router.message(F.text == "➕ Xodim qo'shish")
async def start_add_employee(message: Message, state: FSMContext):
    await state.set_state(EmployeeForm.full_name)
    await message.answer("👤 Xodimning F.I.Sh (Ism va Familiyasi)ni kiriting:")

@router.message(EmployeeForm.full_name)
async def get_emp_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(EmployeeForm.branch)
    await message.answer("🏢 Xodim qaysi filialga tegishli?", reply_markup=branch_select_menu)

@router.message(EmployeeForm.branch)
async def get_emp_branch(message: Message, state: FSMContext):
    branch = message.text
    if branch not in ["Diamond-1", "Diamond-2", "Diamond-3"]:
        await message.answer("⚠️ Iltimos, tugmalardan birini tanlang!")
        return
    await state.update_data(branch=branch)
    await state.set_state(EmployeeForm.position)
    await message.answer("💼 Xodimning lavozimini kiriting (matn ko'rinishida yozing):", reply_markup=None)

@router.message(EmployeeForm.position)
async def get_emp_position(message: Message, state: FSMContext):
    await state.update_data(position=message.text)
    await state.set_state(EmployeeForm.telegram_id)
    await message.answer("🆔 Xodimning Telegram ID raqamini kiriting (agar bilmasangiz 0 yozing):")

@router.message(EmployeeForm.telegram_id)
async def get_emp_tg_id(message: Message, state: FSMContext):
    try:
        tg_id = int(message.text)
    except ValueError:
        tg_id = 0

    data = await state.get_data()
    add_employee(data["full_name"], data["branch"], data["position"], tg_id)
    
    await message.answer(
        f"✅ **Xodim muvaffaqiyatli qo'shildi!**\n\n"
        f"👤 F.I.Sh: {data['full_name']}\n"
        f"🏢 Filial: {data['branch']}\n"
        f"💼 Lavozim: {data['position']}",
        reply_markup=employee_menu
    )
    await state.clear()

@router.message(F.text == "📋 Xodimlar ro'yxati")
async def list_employees(message: Message):
    employees = get_employees()
    if not employees:
        await message.answer("📭 Hozircha xodimlar mavjud emas.")
        return

    for emp in employees:
        text = f"👤 **{emp[1]}**\n🏢 Filial: {emp[2]}\n💼 Lavozim: {emp[3]}\n🆔 Telegram ID: {emp[4]}"
        await message.answer(text, reply_markup=get_employee_inline_kb(emp[0]))

@router.callback_query(F.data.startswith("del_emp_"))
async def delete_emp_cb(call: CallbackQuery):
    emp_id = int(call.data.split("_")[2])
    delete_employee(emp_id)
    await call.message.edit_text("❌ Xodim o'chirildi!")
    await call.answer()

@router.message(F.text == "📊 KPI natijamni ko'rish")
async def show_employee_kpi_report(message: Message):
    tg_id = message.from_user.id
    kpis = get_kpi_by_telegram_id(tg_id)
    
    if not kpis:
        await message.answer("📭 Siz hali hech qanday KPI kiritmagansiz.")
        return
        
    total_score = sum(item[7] for item in kpis)
    await message.answer(f"📊 **Sizning shaxsiy natijalaringiz:**\n⭐️ Jami yig'ilgan ballingiz: {total_score}")
    
    for item in kpis[:10]:
        text = (
            f"📅 Sana: {item[3]} | 💼 Vazifa: {item[4]}\n"
            f"💰 Summa: {item[6]} so'm | ⭐️ Ball: {item[7]}"
        )
        if item[5]:
            try:
                if len(item[5]) > 30 and ("video" in item[4].lower() or "ochilish" in item[4].lower()):
                    await message.answer_video_note(item[5], caption=text)
                else:
                    await message.answer_photo(item[5], caption=text)
            except Exception:
                await message.answer(text)
        else:
            await message.answer(text)

@router.message(F.text == "📊 Haftalik hisobot")
async def show_weekly_report(message: Message):
    tg_id = message.from_user.id
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    emp = get_employee_by_tg_id(tg_id)
    if emp:
        weekly_data = get_weekly_kpi_by_employee(tg_id, start_date, end_date)
        text = f"📅 **Haftalik hisobot** ({start_date} dan {end_date} gacha):\n\n"
        total_w_score = 0
        for row in weekly_data:
            text += f"• {row[0]}: {row[3]} marta | ⭐️ {row[2]} ball\n"
            total_w_score += row[2]
        text += f"\n⭐️ **Jami haftalik ball:** {total_w_score}"
        await message.answer(text)