# - *- coding: utf- 8 - *-
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.data.config import BOT_TEXTS

orders_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Мои заказы"),
        ],
        [
            KeyboardButton(text="Условия доставки"),
            KeyboardButton(text="Оплата доставки"),
        ],
        [
            KeyboardButton(text="Оформление заказа"),
        ],
        [
            KeyboardButton(text="Главное меню"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие из меню",
    selective=True
)

cancel_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Отменить")]], resize_keyboard=True)