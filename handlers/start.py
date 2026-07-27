from aiogram import Router, F
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
    employee = get_employee_by_tg_id(tg_id)

    if tg_id in ADMIN_IDS:
        await message.answer(
            "💎 Diamond KPI BOT\n\nRahbar paneliga xush kelibsiz.",
            reply_markup=boss_menu,
        )
        return

    if employee is None:
        await message.answer(
            "❌ Siz tizimda ro'yxatdan o'tmagansiz."
        )
        return

    await message.answer(
        f"Assalomu alaykum, {employee[1]}!",
        reply_markup=employee_main_menu,
    )


@router.message(F.text == "⬅️ Bosh menyuga qaytish")
async def back_main(message: Message, state: FSMContext):
    await state.clear()
    tg_id = message.from_user.id

    if tg_id in ADMIN_IDS:
        await message.answer(
            "🏠 Rahbar menyusi",
            reply_markup=boss_menu,
        )
    else:
        await message.answer(
            "🏠 Bosh menyu",
            reply_markup=employee_main_menu,
        )