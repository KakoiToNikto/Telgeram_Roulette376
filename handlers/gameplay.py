import asyncio
import textwrap

from aiogram import types, Router
from aiogram.filters import F

from roulette_menu import before_game_menu
from session import GameSession


gameplay_router = Router()


#Тут разобраться и написать функцию, которая будет запускаться после команды play
# - делает сессию и ожидает набора 2-х разных юзеров. После набора начинает игру
# (дальше идут геймплейные функции)