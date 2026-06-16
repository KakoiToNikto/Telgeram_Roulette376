from random import choice

from aiogram import types, Router
from aiogram.filters import F

class GameSession:
    def __init__(self, p1, p2):
        self.players = {
            p1: {"id1": p1.message.chat.id,
                 "hp": 5,
                 "is_alive": True,
                 "is_handcuffed": False,
                 
                },
            p2: {"id2": p2.message.chat.id,
                 "hp": 5}
        }