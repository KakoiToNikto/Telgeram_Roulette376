from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from dotenv import load_dotenv, find_dotenv
import os

from roulette_commands import commands

from handlers.roulette_handler import roulette_handler_router
from handlers.lobby import lobby_router
from handlers.gameplay import gameplay_router


load_dotenv(find_dotenv())
Bot = Bot(token=os.getenv("token"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()
dp.include_router(roulette_handler_router)
dp.include_router(lobby_router)
dp.include_router(gameplay_router)


async def Main():
    await Bot.delete_webhook(drop_pending_updates=True)
    await Bot.set_my_commands(commands=commands, scope=types.BotCommandScopeDefault())
    try:
        await dp.start_polling(Bot)
    except (KeyboardInterrupt, SystemExit):
        print("Остановка бота, системная ошибка. Нужно перезапустить.\nThe bot is stopping, system error. Need to restart.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(Main())