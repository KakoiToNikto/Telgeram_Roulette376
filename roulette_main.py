from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from dotenv import load_dotenv, find_dotenv
import os

from roulette_commands import commands
from roulette_handler import roulette_handler_router

load_dotenv(find_dotenv())
Bot = Bot(token=os.getenv("token"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_router(roulette_handler_router)

async def Main():
    await dp.start_polling(Bot)
    await Bot.delete_webhook(drop_pending_updates=True)
    await Bot.set_my_commands(commands=commands, scope=types.BotCommandScopeDefault())
    # когда пользователь пишет боту в личке, он увидит этот набор команд, а в группе - нет, т.к. там другой scope
    

if __name__ == "__main__":
    import asyncio
    asyncio.run(Main())