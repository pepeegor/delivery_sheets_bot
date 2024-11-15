# - *- coding: utf- 8 - *-
import re
import uuid

from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message, CallbackQuery, ReplyKeyboardMarkup

from bot.keyboards.inline.main_keyboard import registration
from bot.data.config import BOT_TEXTS
from bot.keyboards.reply.main_keyboard import menu_frep, welcome_kb
from bot.services.sheets.sheets_api import User


router = Router()


@router.message(F.text == '/start')
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    loading = await message.answer(BOT_TEXTS.get('loading_text', 'Загрузка...'))
    if User.is_user_auth(message.from_user.id):
        await loading.delete()
        await message.answer(BOT_TEXTS.get('welcome_text'), reply_markup=welcome_kb)
    else:
        await loading.delete()
        await message.answer(BOT_TEXTS.get('welcome_reg_message', 'Привет!'), reply_markup=registration())




@router.callback_query(F.data == 'user_registration')
async def user_reg(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.delete()
    msg = await call.message.answer(BOT_TEXTS.get('loading_text', 'Загрузка...'))
    if not User.is_user_auth(call.from_user.id):
        await msg.delete()
        await call.message.answer(BOT_TEXTS.get('reg_entered_name', 'Введите ваше ФИО:'))
        await state.set_state('get_user_name')


@router.message(StateFilter('get_user_name'))
async def get_user_name(message: Message, state: FSMContext) -> None:
    user_name = message.text

    match = re.match(
        r'^[А-ЯA-Z][а-яa-z]+\s[А-ЯA-Z][а-яa-z]+(\s[А-ЯA-Z][а-яa-z]+(-[А-ЯA-Z][а-яa-z]+)?)?$',
        user_name
    )
    
    if match:
        await state.update_data(user_name=user_name)
        await message.answer(BOT_TEXTS.get('reg_entered_phone', 'Введите ваш номер телефон:'))
        await state.set_state('get_phone_number')
    else:
        await state.set_state('get_user_name')
        await message.answer(BOT_TEXTS.get('reg_invalid_name', 'ФИО не валидно\nВведите ваше ФИ или ФИО:'))


@router.message(StateFilter('get_phone_number'))
async def get_phone(message: Message, state: FSMContext) -> None:
    match = re.match(r'^\+?1?\d{9,15}$', message.text)
    if match:
        await state.update_data(phone=message.text)
        await state.set_state('get_promocode')
        await message.answer(BOT_TEXTS.get('enter_promocode', 'Введите промокод (если есть) или нажмите "Пропустить"'), 
                           reply_markup=ReplyKeyboardMarkup(
                               keyboard=[[KeyboardButton(text="Пропустить")]],
                               resize_keyboard=True,
                               one_time_keyboard=True
                           ))
    else:
        await state.set_state('get_phone_number')
        await message.answer(BOT_TEXTS.get('reg_invalid_phone', 'Номер телефона не валиден\nВведите номер телефона:'))


@router.message(StateFilter('get_promocode'))
async def get_promocode(message: Message, state: FSMContext) -> None:
    user_data = await state.get_data()
    username = user_data['user_name']
    phone = user_data['phone']
    promocode = "" if message.text == "Пропустить" else message.text
    
    load = await message.answer(BOT_TEXTS.get('loading_text', 'Загрузка...'))
    User.add_user(message.from_user.id, username, phone, User.get_next_id(), promocode)
    await state.clear()
    await load.delete()
    success = await message.answer(BOT_TEXTS.get('reg_sucessful', 'Вы зарегистрированы'))
    await success.delete()
    await message.answer(BOT_TEXTS.get('welcome_text'), reply_markup=welcome_kb)