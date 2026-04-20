import asyncio
from aiogram import Bot, Dispatcher
import os
from tg_bot.handlers import start, user, navigation
from tg_bot.handlers.titles import add_titles, watch_titles
from tg_bot.handlers.watchlist import add_watchlist, watch_watchlist

bot = Bot(token=os.getenv("BOT_TOKEN"))

dp = Dispatcher()


async def main():
    # Начинаем слушать сервера Телеграма (Polling)
    dp.include_router(start.router)
    dp.include_router(navigation.router)
    dp.include_router(add_titles.router)
    dp.include_router(add_watchlist.router)
    dp.include_router(watch_watchlist.router)
    dp.include_router(user.router)
    dp.include_router(watch_titles.router)

    await dp.start_polling(bot, handle_signals=False)

def start_bot_thread():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except Exception as e:
        print('ERROR in start_bot_thread()')
        print(e)

if __name__ == "__main__":
    asyncio.run(main())
