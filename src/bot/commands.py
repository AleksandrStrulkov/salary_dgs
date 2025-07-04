import os
from dotenv import load_dotenv
from aiogram import Router, F, Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from bot.keyboards import show_full_result_kb, main_menu_kb, main_menu_start, get_back_finish_kb, combined_keyboard

router = Router()
used_users = set()
ADMIN_ID = int(os.getenv("ADMIN_ID"))
load_dotenv()


@router.message(Command("start"))
async def start_handler(message: Message):
    used_users.add(message.from_user.id)
    await message.answer(
            "👋 *Привет!*\n"
            "🚀 Я посчитаю *Вашу зарплату!* Выберите действие:",
            reply_markup=main_menu_kb, parse_mode="Markdown"
    )


@router.message(Command("stats"))
async def stats_handler(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(
                f"👥 Пользователей воспользовалось ботом: {len(used_users)}"
        )
    else:
        await message.answer("⛔️ Недостаточно прав.")


@router.message(Command("help"))
async def stats_handler(message: Message):
    await message.answer(
            f"*1. ПРЕМИЯ:*\n"
            "От базового оклада - *40%*\n\n"
            "*2. ДОПЛАТА ЗА РАБОТУ В НОЧНОЕ ВРЕМЯ:*\n"
            "От базового оклада за фактически отработанное время - *20%*\n"
            "В ночную смену - *6ч.*\n"
            "В вечернюю смену - *1,3ч.*\n\n"
            "*3. НАДБАВКА ЗА ВРЕДНЫЕ УСЛОВИЯ ТРУДА:*\n"
            "От базового оклада - *4%*\n\n"
            "*4. ДОПЛАТА ЗА РАБОТУ В ВЫРАБОТКАХ С ТЕМПРЕТУРОЙ ВОЗДУХА ОТ +26 ДО +30С:*\n"
            "От базового оклада - *10%*\n\n"
            "*5. РАЙОННЫЙ КОЭФФИЦИЕНТ:*\n"
            "Пункты расчета 1,2,3,4 суммируются,\n"
            "и применяется надбавка от этой суммы - *30%*\n\n"
            "*6. СЕВЕРНАЯ НАДБАВКА:*\n"
            "Пункты расчета 1,2,3,4 суммируются,\n"
            "и применяется надбавка от этой суммы - *50%*\n\n"
            "*7. ОПЛАТА В ДВОЙНОМ РАЗМЕРЕ:*\n"
            "Разница между фактически отработанными днями и нормой\n"
            "рабочего времени за месяц оплачивается в двойном размере.\n"
            "Первая оплата - в месяц расчета со всеми надбавками,\n"
            "Вторая оплата - в расчетный период квартала без надбавок.\n\n"
            "*8. НАЛОГОВЫЙ ВЫЧЕТ НА ДЕТЕЙ:*\n"
            "На первого ребенка - *1400 ₽*\n"
            "На второго ребенка - *1600 ₽*\n"
            "На третьего ребенка и последующих - *6000 ₽*\n"
            "Если на первого ребенка налоговый вычет уже не производится, "
            " то на последующих детей сумма вычета не меняется.\n"
            "Стоит учитывать, что налоговый вычет на детей\n*не является постоянным!*\n"
            "Предельный доход, при получении которого у физических лиц сохраняется право "
            " на получение таких вычетов составляет:\n- *450 000 ₽*", parse_mode="Markdown"
    )