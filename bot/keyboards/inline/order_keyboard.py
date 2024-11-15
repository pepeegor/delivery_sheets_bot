import math

from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton as ikb
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.data.config import BOT_TEXTS
from bot.services.sheets.sheets_api import Order


def order_keyboard(remover) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    get_orders = Order.get_orders()
    if len(get_orders) == 0:
        keyboard.row(
            ikb(
                text="Пока заказов нет...",
                callback_data="..."
            )
        )
    else:
        if 10 - (len(get_orders) % 10) != 10:
            remover_page = len(get_orders) + (10 - (len(get_orders) % 10))
        else:
            remover_page = len(get_orders)

        if remover >= len(get_orders): remover -= 10

        for count, a in enumerate(range(remover, len(get_orders))):
            if count < 10:
                keyboard.row(
                    ikb(text=
                        '#' + get_orders[a][2] + ' ' + get_orders[a][3] + ' - '+ get_orders[a][4],
                        callback_data=f"order_open:{a}",
                    )
                )

        if len(get_orders) <= 10:
            ...
        elif len(get_orders) > 10 and remover < 10:
            if len(get_orders) > 20:
                keyboard.row(
                    ikb(text=f"1/{math.ceil(len(get_orders) / 10)}", callback_callback_data="..."),
                    ikb(text="»", callback_data=f"swipe_order:{remover + 10}"),
                    ikb(text="⏩", callback_data=f"swipe_order:{remover_page}"),
                )
            else:
                keyboard.row(
                    ikb(text=f"1/{math.ceil(len(get_orders) / 10)}", callback_data="..."),
                    ikb(text="»", callback_data=f"swipe_order:{remover + 10}")
                )
        elif remover + 10 >= len(get_orders):
            if len(get_orders) > 20:
                keyboard.row(
                    ikb(text="⏪", callback_data=f"swipe_order:0"),
                    ikb(text="	«", callback_data=f"swipe_order:{remover - 10}"),
                    ikb(text=f"{str(remover + 10)[:-1]}/{math.ceil(len(get_orders) / 10)}", callback_data="..."),
                )
            else:
                keyboard.row(
                    ikb(text="	«", callback_data=f"swipe_order:{remover - 10}"),
                    ikb(text=f"{str(remover + 10)[:-1]}/{math.ceil(len(get_orders) / 10)}", callback_data="...")
                )
        else:
            if len(get_orders) > 20:
                if remover >= 20:
                    keyboard.row(
                        ikb(text="⏪", callback_data=f"swipe_order:0"),
                        ikb(text="	«", callback_data=f"swipe_order:{remover - 10}"),
                        ikb(text=f"{str(remover + 10)[:-1]}/{math.ceil(len(get_orders) / 10)}", callback_data="..."),
                        ikb(text="»", callback_data=f"swipe_order:{remover + 10}"),
                    )
                else:
                    keyboard.row(
                        ikb(text="	«", callback_data=f"swipe_order:{remover - 10}"),
                        ikb(text=f"{str(remover + 10)[:-1]}/{math.ceil(len(get_orders) / 10)}", callback_data="..."),
                        ikb(text="»", callback_data=f"swipe_order:{remover + 10}"),
                    )

                if remover_page - 20 > remover:
                    keyboard.add(
                        ikb(text="⏩", callback_data=f"swipe_order:{remover_page}"),
                    )
            else:
                keyboard.row(
                    ikb(text="	«", callback_data=f"swipe_order:{remover - 10}"),
                    ikb(text=f"{str(remover + 10)[:-1]}/{math.ceil(len(get_orders) / 10)}", callback_data="..."),
                    ikb(text="»", callback_data=f"swipe_order:{remover + 10}"),
                )

        keyboard.row(
            ikb(text=BOT_TEXTS.get('home_menu_order_contact', 'Связь с менеджером'), url=BOT_TEXTS.get('home_menu_order_contact_url', '?')),
        )

    return keyboard.as_markup()