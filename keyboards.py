from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Rahbar uchun menyu (Xodimlar, Hisobotlar, Excel - KPI kiritish yo'q)
boss_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👥 Xodimlar"), KeyboardButton(text="📊 KPI hisobotlarini ko'rish")],
        [KeyboardButton(text="📥 Excel hisobot")]
    ],
    resize_keyboard=True
)

# Xodim uchun menyu (Faqat KPI kiritish va natijani bilish)
employee_main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 KPI kiritish"), KeyboardButton(text="📊 KPI natijamni ko'rish")]
    ],
    resize_keyboard=True
)

employee_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Xodim qo'shish"), KeyboardButton(text="📋 Xodimlar ro'yxati")],
        [KeyboardButton(text="⬅️ Bosh menyuga qaytish")]
    ],
    resize_keyboard=True
)

branch_select_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Diamond-1"), KeyboardButton(text="Diamond-2")],
        [KeyboardButton(text="Diamond-3")],
        [KeyboardButton(text="⬅️ Bosh menyuga qaytish")]
    ],
    resize_keyboard=True
)

kpi_tasks_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📹 Har kuni ochilish videosi")],
        [KeyboardButton(text="🧹 Tozalik va tartib (10 ball)")],
        [KeyboardButton(text="📱 Instagram post"), KeyboardButton(text="📸 Instagram stories")],
        [KeyboardButton(text="👀 3000+ ko'rish"), KeyboardButton(text="💰 Savdo rejasi")],
        [KeyboardButton(text="📉 Qarzdorlik oshmasligi"), KeyboardButton(text="🎁 Bonus me'yoridan oshmasligi")],
        [KeyboardButton(text="⬅️ Bosh menyuga qaytish")]
    ],
    resize_keyboard=True
)

def get_employee_inline_kb(emp_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Xodimni o'chirish", callback_data=f"del_emp_{emp_id}")]
        ]
    )

# Rahbar uchun KPI tahrirlash va o'chirish tugmalari
def get_kpi_boss_inline_kb(kpi_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ Tahrirlash (Ball)", callback_data=f"edit_kpi_{kpi_id}"),
                InlineKeyboardButton(text="❌ O'chirish", callback_data=f"del_kpi_{kpi_id}")
            ]
        ]
    )