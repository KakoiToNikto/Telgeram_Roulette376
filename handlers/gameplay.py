import asyncio
import textwrap

from aiogram import types, Router, F

from roulette_menu import before_game_menu, actions_menu, items_menu
from .session import GameSession
from .tracking import active_games


gameplay_router = Router()

#фильтр, чтобы каждый игрок ходил по очереди
async def start_round(state):
    pass


@gameplay_router.message()
async def choose_actions():
    pass
    #тут будет показываться actions_menu

#----------------------------------------------------------------------------------
async def shoot_logic(bot, game_data: GameSession, player_id: int, shoot_enemy: bool, current_player):
    #реализовать проверку, связанные с предметами(наручники, поджигательные снаряды и пр.) + добавить провеику текущего игрока
    enemy_id = game_data.player2 if player_id == game_data.player1 else game_data.player1
    enemy_username = (await bot.get_chat(enemy_id)).username
    player_username = (await bot.get_chat(player_id)).username

    if game_data.current_player != player_id:
        return
    
    await bot.send_message(chat_id=game_data.chat_id, text=f"Игрок {player_username} делает выстрел {'в противника' if shoot_enemy else 'в себя'}...")
    await asyncio.sleep(1.5)      

    if game_data.bullets.pop() == 0:
        await bot.send_message(chat_id=game_data.chat_id, text=f"Патрон был холостой! C игроком {player_username} все впорядке!\nКоличество оставшихся жизней: {game_data.players[player_id]['hp']}")
        await asyncio.sleep(1)
    else:
        game_data.bullets.pop()
        if shoot_enemy:
            game_data.players[enemy_id]["hp"] -= 1
            await bot.send_message(chat_id=game_data.chat_id, text=f"Патрон настоящий, и он попал прямо в {enemy_username}\nКоличество оставшихся жизней у {enemy_username}: <b>{game_data.players[enemy_id]['hp']}</b>")
            if game_data.players[enemy_id]["hp"] <= 0:
                await bot.send_message(chat_id=game_data.chat_id, text=f"Этот день оказался последним для тебя, {enemy_username}...\nТы храбро играл, но вышел из игры проигравшим.😔\n<b>{player_username}, поздравляю тебя с победой!</b>\nКОНЕЦ ИГРЫ💯")
                #тут еще нужно добавить позже итоговую таблицу на каждого игрока: всего ходов, использованно предмтов и пр.
        else:
            game_data.players[player_id]["hp"] -= 1
            await bot.send_message(chat_id=game_data.chat_id, text=f"Патрон настоящий, и он попал прямо в {player_username}\nКоличество оставшихся жизней у {player_username}: <b>{game_data.players[player_id]['hp']}</b>")
            if game_data.players[player_id]["hp"] <= 0:
                await bot.send_message(chat_id=game_data.chat_id, text=f"Этот день оказался последним для тебя, {player_username}...\nТы храбро играл, но вышел из игры проигравшим.😔\n<b>{enemy_username}, поздравляю тебя с победой!</b>\nКОНЕЦ ИГРЫ💯")
                #тут еще нужно добавить позже итоговую таблицу на каждого игрока: всего ходов, использованно предмтов и пр.


@gameplay_router.callback_query(F.data == "shoot_enemy")
async def shoot_enemy(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    game_data: GameSession = active_games[chat_id]

    await shoot_logic(call.bot, game_data, call.from_user.id, shoot_enemy=True)

@gameplay_router.callback_query(F.data == "shoot_myself")
async def shoot_myself(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    game_data: GameSession = active_games[chat_id]

    await shoot_logic(call.bot, game_data, call.from_user.id, shoot_enemy=False)



@gameplay_router.callback_query(F.data == "Bint")
async def use_bint(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    game_data: GameSession = active_games[chat_id]

    await call.answer("Бинт выбран")
    await call.message.answer(f"[Заготовка] Предмет 'Бинт' для {call.from_user.username} будет реализован позже.")


@gameplay_router.callback_query(F.data == "Magnet")
async def use_magnet(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    game_data: GameSession = active_games[chat_id]

    await call.answer("Магнит выбран")
    await call.message.answer(f"[Заготовка] Предмет 'Магнит' для {call.from_user.username} будет реализован позже.")


@gameplay_router.callback_query(F.data == "magnifying_glass")
async def use_magnifying_glass(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    game_data: GameSession = active_games[chat_id]

    await call.answer("Лупа выбран")
    await call.message.answer(f"[Заготовка] Предмет 'Лупа' для {call.from_user.username} будет реализован позже.")


@gameplay_router.callback_query(F.data == "fire_bullet")
async def use_fire_bullet(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    game_data: GameSession = active_games[chat_id]

    await call.answer("Зажигательный снаряд выбран")
    await call.message.answer(f"[Заготовка] Предмет 'Зажигательный снаряд' для {call.from_user.username} будет реализован позже.")


@gameplay_router.callback_query(F.data == "handcuffes")
async def use_handcuffes(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    game_data: GameSession = active_games[chat_id]

    await call.answer("Наручники выбраны")
    await call.message.answer(f"[Заготовка] Предмет 'Наручники' для {call.from_user.username} будет реализован позже.")


#------------------------------------------------------------------------------------
def is_game_over(self, chat_id, players: dict) -> bool:
    pass

#дописать логигу gameplay, функции и все меню