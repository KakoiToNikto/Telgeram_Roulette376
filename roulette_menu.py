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

def actions_menu():
    menu = InlineKeyboardBuilder()
    menu.row(
        InlineKeyboardButton(text="Выстрелить в противника", callback_data="shoot_emeny"),
        InlineKeyboardButton(text="Выстрелить в себя", callback_data="shoot_myself"),
    )
    menu.row(
        InlineKeyboardButton(text="Использовать предметы", callback_data="use_items"),
    )
    return menu.as_markup()

def items_menu():
    menu = InlineKeyboardBuilder()
    menu.row(
        InlineKeyboardButton(text=f"Бинт({bint_count}шт.)", callback_data="Bint"),
        InlineKeyboardButton(text=f"Магнит({magnet_count})", callback_data="Magnet")
    )
    menu.row(
        InlineKeyboardButton(text=f"Лупа({magnifying_glass_count}шт.)", callback_data="magnifying_glass"),
        InlineKeyboardButton(text=f"Зажиг-ый снаряд({fire_bullet_count})", callback_data="fire_bullet")
    )
    menu.row(
        InlineKeyboardButton(text=f"Наручники({handcuffes_count}шт.)", callback_data="handcuffes"),
    )
    return menu.as_markup()

#импортировать все подсчеты предметов, сделать после реализации use_items