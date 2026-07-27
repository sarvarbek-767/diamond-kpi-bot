from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import ADMIN_IDS
from database import get_employee_by_tg_id
from keyboards import boss_menu, employee_main_menu

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    tg_id = message.from_user.id
    emp = get_employee_by_tg_id(tg_id)
    
    if not emp and tg_id not in ADMIN_IDS:
        await message.answer("⚠️ Siz ro'yxatdan o'tmagansiz va rahbar emassiz.")
        return
        
    if tg_id in ADMIN_IDS:
        await message.answer(
            "💎 **Diamond KPI BOT** — Rahbar paneliga xush kelibsiz!",
            reply_markup=boss_menu
        )
    else:
        await message.answer(
            f"💎 **Diamond KPI BOT** — Xush kelibsiz, {emp[1]}!\n"
            f"Filialingiz: {emp[2]}",
            reply_markup=employee_main_menu
        )

@router.message(F.text == "⬅️ Bosh menyuga qaytish")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    tg_id = message.from_user.id
    
    if tg_id in ADMIN_IDS:
        await message.answer("🏠 Rahbar menyusi:", reply_markup=boss_menu)
    else:
        await message.answer("🏠 Bosh menyu:", reply_markup=employee_main_menu)