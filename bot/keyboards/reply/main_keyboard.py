# - *- coding: utf- 8 - *-
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.data.config import BOT_TEXTS

welcome_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Мой профиль"),
            KeyboardButton(text="Главное меню"),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие из меню",
    selective=True
)

profile_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Редактировать профиль"),
        ],
        [
            KeyboardButton(text="Главное меню"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие из меню",
    selective=True
)

def menu_frep() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()

    keyboard.row(
        KeyboardButton(text=BOT_TEXTS.get('home_menu_how_to_order_button', "Как заказать?")),
        KeyboardButton(text=BOT_TEXTS.get('home_menu_order_button', 'Доставка'))
    ).row(
        KeyboardButton(text=BOT_TEXTS.get('home_menu_faq_button', 'О нас')),
        KeyboardButton(text=BOT_TEXTS.get('home_menu_problem_button', 'Сообщить о проблеме'))
    ).row(
        KeyboardButton(text=BOT_TEXTS.get('home_menu_panda_premium_button', 'Panda Premium'))
    ).row(
        KeyboardButton(text="Назад")
    )
    return keyboard.as_markup(resize_keyboard=True)