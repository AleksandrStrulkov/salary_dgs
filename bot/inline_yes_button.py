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
        inline_keyboard=[
                [
                        InlineKeyboardButton(text="🔙 Назад", callback_data="go_back"),
                        InlineKeyboardButton(text="Завершить", callback_data="finish"),
                ],
        ]
)

show_months_of_years = InlineKeyboardMarkup(
        inline_keyboard=[
                [
                        InlineKeyboardButton(text="Январь", callback_data="month_january"),
                        InlineKeyboardButton(text="Февраль", callback_data="month_february"),
                        InlineKeyboardButton(text="Март", callback_data="month_march"),
                ],
                [
                        InlineKeyboardButton(text="Апрель", callback_data="month_april"),
                        InlineKeyboardButton(text="Май", callback_data="month_may"),
                        InlineKeyboardButton(text="Июнь", callback_data="month_june"),
                ],
                [
                        InlineKeyboardButton(text="Июль", callback_data="month_july"),
                        InlineKeyboardButton(text="Август", callback_data="month_august"),
                        InlineKeyboardButton(text="Сентябрь", callback_data="month_september"),
                ],
                [
                        InlineKeyboardButton(text="Октябрь", callback_data="month_october"),
                        InlineKeyboardButton(text="Ноябрь", callback_data="month_november"),
                        InlineKeyboardButton(text="Декабрь", callback_data="month_december"),
                ],
        ]
)