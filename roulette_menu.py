from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup)

def roulette_menu_ruler():
    menu = InlineKeyboardBuilder()
    menu.row(
        InlineKeyboardButton(text="Играть💥", callback_data="play"),
        InlineKeyboardButton(text="Статистика 📊", callback_data="stats")
        )
    menu.row(
        InlineKeyboardButton(text="Правила 📜", callback_data="rules")
    )

    return menu.as_markup()


def get_back_menu():
    menu = InlineKeyboardBuilder()
    menu.row(
        InlineKeyboardButton(text="Назад 🔙", callback_data="back")
    )

    return  menu.as_markup()

def before_game_menu():
    menu = InlineKeyboardBuilder()
    menu.row(
    InlineKeyboardButton(text="Вступить в игру", callback_data="get_game"),
    InlineKeyboardButton(text="Отменить подбор игроков 🔙", callback_data="break_game")
)
    return menu.as_markup()
