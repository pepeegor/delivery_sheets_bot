# - *- coding: utf- 8 - *-
import asyncio
import os
import sys
import colorama


from bot.data.loader import bot, dp

colorama.init()


async def main():
    try:
        print(colorama.Fore.LIGHTBLUE_EX + f"~~~~~ Bot was started - @{(await bot.get_me()).username} ~~~~~")
        print(colorama.Fore.LIGHTCYAN_EX + "~~~~~ kwork.ru/user/gurupythondev ~~~~~")
        print(colorama.Fore.RESET)

        await bot.delete_webhook()
        await bot.get_updates(offset=-1)
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types()
        )
    finally:
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    finally:
        if sys.platform.startswith("win"):
            os.system("cls")
        else:
            os.system("clear")
