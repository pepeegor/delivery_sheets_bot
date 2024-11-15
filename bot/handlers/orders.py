import re
from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.data.config import BOT_TEXTS
from bot.keyboards.inline.order_keyboard import order_keyboard
from bot.keyboards.reply.main_keyboard import menu_frep 
from bot.keyboards.reply.order_keyboard import orders_kb, cancel_kb
from bot.services.sheets.sheets_api import User, Order
from bot.services.states import OrderStates


router = Router()



@router.message(F.text == "Отменить")
async def cancel_order(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Оформление заказа отменено", reply_markup=orders_kb)

@router.message(F.text == BOT_TEXTS.get('home_menu_order_button', 'Доставка'))
async def order_handler(message: Message, state: FSMContext) -> None:
    await state.clear()

    await message.answer(BOT_TEXTS.get('home_menu_order_text'), reply_markup=orders_kb)
    
    
@router.message(F.text == "Оплата доставки")
async def payment_handler(message: Message, state: FSMContext) -> None:
    await state.clear()

    await message.answer(BOT_TEXTS.get('home_menu_order_payment_text'), reply_markup=orders_kb)


@router.message(F.text == "Условия доставки")
async def conditions_handler(message: Message, state: FSMContext) -> None:
    await state.clear()

    await message.answer(BOT_TEXTS.get('home_menu_conditions_text'))


@router.message(F.text == "Оформление заказа")
async def start_order(message: Message, state: FSMContext) -> None:
    await state.set_state(OrderStates.track_codes)
    await message.answer("Если у вас несколько товаров - указывайте несколько трэк-кодов\n\nОбувь создавайте отдельным заказом!")
    await message.answer("Введите трек-код(ы) через запятую:", reply_markup=cancel_kb)

@router.message(OrderStates.track_codes)
async def get_track_codes(message: Message, state: FSMContext) -> None:
    track_codes = [code.strip() for code in message.text.split(',')]
    await state.update_data(track_codes=track_codes)
    await state.set_state(OrderStates.name)
    await message.answer("Введите ФИО:")

@router.message(OrderStates.name) 
async def get_name(message: Message, state: FSMContext) -> None:
    user_name = message.text
    match = re.match(
        r'^[А-ЯA-Z][а-яa-z]+\s[А-ЯA-Z][а-яa-z]+(\s[А-ЯA-Z][а-яa-z]+(-[А-ЯA-Z][а-яa-z]+)?)?$',
        user_name
    )
    if match:
        await state.update_data(name=user_name)
        await message.answer(BOT_TEXTS.get('reg_entered_phone', 'Введите ваш номер телефон:'))
        await state.set_state(OrderStates.phone)
    else:
        await state.set_state(OrderStates.name)
        await message.answer(BOT_TEXTS.get('reg_invalid_name', 'ФИО не валидно\nВведите ваше ФИ или ФИО:'))

@router.message(OrderStates.phone)
async def get_phone(message: Message, state: FSMContext) -> None:
    match = re.match(r'^\+?1?\d{9,15}$', message.text)
    if match:
        await state.set_state(OrderStates.address)
        await state.update_data(phone=message.text)
        await message.answer("Введите адрес ПВЗ СДЭКа:")
    else:
        await state.set_state(OrderStates.phone)
        await message.answer(BOT_TEXTS.get('reg_invalid_phone', 'Номер телефона не валиден\nВведите номер телефона:'))

@router.message(OrderStates.address)
async def get_address(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    track_codes = data['track_codes']
    name = data['name']
    phone = data['phone']
    address = message.text

    await message.answer(BOT_TEXTS.get('loading_text', 'Загрузка...'))

    user_data = User.get_user_data(message.from_user.id)
    status = "Более подробный" if user_data.get('status') == "PandaPremium" else "В пути"

    Order.add_order(track_codes[0], status, name, phone, address, message.from_user.id)

    if len(track_codes) > 1:
        for track_code in track_codes[1:]:
            Order.add_additional_track(track_code)

    await state.clear()
    await message.answer("Заказ успешно оформлен!", reply_markup=orders_kb)
    
    
@router.message(F.text == "Мои заказы")
async def show_user_orders(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    
    await message.answer(BOT_TEXTS.get('loading_text', 'Загрузка...'))
    
    all_orders = Order.get_orders()
    
    if not all_orders:
        await message.answer("У вас пока нет заказов.", reply_markup=orders_kb)
        return
    
    current_order = None
    user_orders = []
    
    for row in all_orders:
        if not row:
            continue
            
        if len(row) >= 7 and row[0] and row[2] and row[3] and str(row[6]) == str(user_id):
            if current_order:
                user_orders.append(current_order)
            current_order = {
                "order_id": row[0],
                "track_codes": [row[1]] if row[1] else [],
                "status": row[2],
                "name": row[3],
                "phone": f"+{row[4]}",
                "address": row[5]
            }
        elif current_order and len(row) >= 2 and row[1] and not row[0]:
            current_order["track_codes"].append(row[1])
    
    if current_order:
        user_orders.append(current_order)
    
    if not user_orders:
        await message.answer("У вас пока нет заказов.", reply_markup=orders_kb)
        return
    
    response = "Ваши заказы:\n\n"
    for order in user_orders:
        track_codes_str = "\n".join([f"• {code}" for code in order["track_codes"]])
        
        response += (f"Заказ №{order['order_id']}\n"
                    f"Трек-коды:\n{track_codes_str}\n"
                    f"Статус: {order['status']}\n"
                    f"ФИО: {order['name']}\n"
                    f"Телефон: {order['phone']}\n"
                    f"Адрес ПВЗ СДЭКА: {order['address']}\n\n")

    if len(response) > 4096:
        parts = [response[i:i+4096] for i in range(0, len(response), 4096)]
        for part in parts:
            await message.answer(part, reply_markup=orders_kb)
    else:
        await message.answer(response, reply_markup=orders_kb)




