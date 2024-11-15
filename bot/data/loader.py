# - *- coding: utf- 8 - *-
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.data.config import BOT_TOKEN
from bot.handlers import main_start
from bot.handlers import main
from bot.handlers import orders
from bot.handlers import profile

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

dp.include_routers(
    main_start.router,
    main.router,
    orders.router,
    profile.router,
)