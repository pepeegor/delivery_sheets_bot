import re
from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message, CallbackQuery, ReplyKeyboardMarkup

from bot.data.config import BOT_TEXTS
from bot.keyboards.inline.order_keyboard import order_keyboard
from bot.keyboards.reply.main_keyboard import profile_kb
from bot.services.sheets.sheets_api import User, Order


router = Router()


@router.message(F.text == "Мой профиль")
async def profile_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(BOT_TEXTS.get('loading_text', 'Загрузка...'))
    user_data = User.get_user_data(message.from_user.id)
    await message.answer(
        f"ФИО - {user_data['user_name']}\n"
        f"Номер - +{user_data['user_phone']}\n"
        f"ID - {user_data['panda_id']}\n"
        f"Статус: {user_data['status']}",
        reply_markup=profile_kb
    )

@router.message(F.text == "Редактировать профиль")
async def edit_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state("edit_user_name")
    User.clear_user_info(message.from_user.id)
    await message.answer(BOT_TEXTS.get('reg_entered_name', 'Введите ваше ФИО:'))
    
    
@router.message(StateFilter('edit_user_name'))
async def edit_user_name(message: Message, state: FSMContext) -> None:
    user_name = message.text

    match = re.match(
        r'^[А-ЯA-Z][а-яa-z]+\s[А-ЯA-Z][а-яa-z]+(\s[А-ЯA-Z][а-яa-z]+(-[А-ЯA-Z][а-яa-z]+)?)?$',
        user_name
    )
    
    if match:
        await state.update_data(user_name=user_name)
        await message.answer(BOT_TEXTS.get('reg_entered_phone', 'Введите ваш номер телефон:'))
        await state.set_state('edit_phone_number')
    else:
        await state.set_state('edit_user_name')
        await message.answer(BOT_TEXTS.get('reg_invalid_name', 'ФИО не валидно\nВведите ваше ФИ или ФИО:'))


@router.message(StateFilter('edit_phone_number'))
async def edit_phone(message: Message, state: FSMContext) -> None:
    match = re.match(r'^\+?1?\d{9,15}$', message.text)
    if match:
        user_name = await state.get_data()
        username = user_name['user_name']
        await message.answer(BOT_TEXTS.get('loading_text', 'Загрузка...'))
        User.update_user_info(message.from_user.id, username, message.text)
        user_data = User.get_user_data(message.from_user.id)
        await message.answer(
            "Вы успешно отредактировали свой профиль."
        )
        await message.answer(
            f"ФИО - {user_data['user_name']}\n"
            f"Номер - +{user_data['user_phone']}\n"
            f"ID - {user_data['panda_id']}\n"
            f"Статус: {user_data['status']}",
            reply_markup=profile_kb
        )
        await state.clear()
    else:
        await state.set_state('edit_phone_number')
        await message.answer(BOT_TEXTS.get('reg_invalid_phone', 'Номер телефона не валиден\nВведите номер телефона:'))


