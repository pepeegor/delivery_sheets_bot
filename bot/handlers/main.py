# - *- coding: utf- 8 - *-
import re

from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.data.config import BOT_TEXTS
from bot.keyboards.inline.order_keyboard import order_keyboard
from bot.keyboards.reply.main_keyboard import menu_frep, welcome_kb
from bot.services.sheets.sheets_api import User, Order


router = Router()


@router.message(F.text == "Главное меню")
async def welcome_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(BOT_TEXTS.get('home_menu_text', 'Главное меню'), reply_markup=menu_frep())
    

@router.message(F.text == "Назад")
async def welcome_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(BOT_TEXTS.get('welcome_text'), reply_markup=welcome_kb)


@router.message(F.text == BOT_TEXTS.get('home_menu_faq_button', 'О нас'))
async def faq_handler(message: Message, state: FSMContext) -> None:
    await state.clear()

    await message.answer(BOT_TEXTS.get('home_menu_faq_text'))
    await message.answer(BOT_TEXTS.get('home_menu_faq_text2'))


@router.message(F.text == BOT_TEXTS.get('home_menu_panda_premium_button'))
async def whats_handler(message: Message, state: FSMContext) -> None:
    await state.clear()

    await message.answer(BOT_TEXTS.get('home_menu_panda_premium_text'))


@router.message(F.text == BOT_TEXTS.get('home_menu_how_to_order_button', "Как заказать?"))
async def support_handler(message: Message, state: FSMContext) -> None:
    await state.clear()

    await message.answer(BOT_TEXTS.get('home_menu_how_to_order_text'))


@router.message(F.text == BOT_TEXTS.get('home_menu_problem_button', 'Сообщить о проблеме'))
async def paid_handler(message: Message, state: FSMContext) -> None:
    await state.clear()

    await message.answer(BOT_TEXTS.get('home_menu_problem_text'))


