from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


main_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Начать", callback_data="start")],
        [InlineKeyboardButton(text="⛔️ Стоп", callback_data="stop")],
    ]
)

show_full_result_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Показать полный расчёт", callback_data="show_full_result"
            ),
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="go_back"),
            InlineKeyboardButton(text="Завершить", callback_data="finish"),
        ],
    ]
)

back_button_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="go_back")]]
)
