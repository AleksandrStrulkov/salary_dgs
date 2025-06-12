from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

show_full_result_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Показать полный расчёт",
                callback_data="show_full_result"
            )
        ]
    ]
)