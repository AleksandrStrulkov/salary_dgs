import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import asyncio
from decimal import Decimal

from bot.states import SalaryInput

TOKEN = os.getenv("BOT_TOKEN")

logger = logging.getLogger(__name__)
logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# 🟢 Стартовая команда
@dp.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    try:
        await state.set_state(SalaryInput.base_salary)
        await message.answer("Привет! Давай рассчитаем вашу зарплату!\n\nВведите ваш оклад:")
        logging.info(f"Оклад задан: {message.text} - {message.from_user.username} - {message.date}")
    except ValueError as error:
        await message.answer(f"Ошибка: {error}")
        logging.error(f"Ошибка при вводе оклада: {error} - {message.from_user.username} - {message.date}")


# 💰 Сбор: оклад
@dp.message(StateFilter(SalaryInput.base_salary))
async def input_base_salary(message: Message, state: FSMContext):
    try:
        await message.answer("Введите ваш оклад: ")
        await state.set_state(SalaryInput.base_salary)
        logging.info("Оклад задан пользователем")
    except ValueError as error:
        await message.answer(f"Ошибка: {error}")
        logging.error(f"Ошибка при вводе оклада: {error}")


# Сбор: месяц
@dp.message(StateFilter(SalaryInput.month))
async def input_month(message: Message, state: FSMContext):
    try:
        await message.answer("Введите месяц расчета (например: июнь: ")
        await state.set_state(SalaryInput.month)
        logging.info("Месяц задан пользователем")
    except ValueError as error:
        await message.answer(f"Ошибка: {error}")
        logging.error(f"Ошибка: {error}")


# Сбор: количество отработанных дней
@dp.message(StateFilter(SalaryInput.sum_days))
async def input_sum_days(message: Message, state: FSMContext):
    pass


# Сбор: количество ночных смен
@dp.message(StateFilter(SalaryInput.night_shifts))
async def input_night_shifts(message: Message, state: FSMContext):
    pass


# Сбор: количество ночных смен
@dp.message(StateFilter(SalaryInput.evening_shifts))
async def input_evening_shifts(message: Message, state: FSMContext):
    pass


