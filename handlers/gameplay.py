import asyncio
import textwrap

from aiogram import types, Router, F

from roulette_menu import before_game_menu
from .session import GameSession


gameplay_router = Router()

