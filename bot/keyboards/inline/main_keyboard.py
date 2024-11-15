from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton as ikb
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.data.config import BOT_TEXTS


def registration() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.row(
        ikb(text=BOT_TEXTS.get('welcome_registration_button', 'Зарегистрироваться'), callback_data="user_registration"),
    )

    return keyboard.as_markup()