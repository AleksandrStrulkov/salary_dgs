import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, Router, types

TOKEN = getenv("BOT_TOKEN")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = Router()
dp = Dispatcher()


@dp.message(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет!")