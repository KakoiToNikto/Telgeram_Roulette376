import asyncio
import textwrap

from aiogram import types, Router, F

from ..roulette_main import Bot
from roulette_menu import before_game_menu
from .session import GameSession
from .tracking import active_games


gameplay_router = Router()




async def shoot_logic(game_data: GameSession, player_id: int, shoot_enemy: bool):
    #реализовать проверку, связанные с предметами(наручники, поджигательные снаряды и пр.)
    enemy_id = game_data.player2 if player_id == game_data.player1 else game_data.player1
    enemy_username = (Bot.get_chat(enemy_id)).username
    player_username = (Bot.get_chat(player_id)).username

    if game_data.current_player != player_id:
        return
    
    await Bot.send_message(chat_id=game_data.chat_id, text=f"Игрок {(Bot.get_chat(player_id)).username} делает выстрел {'в противника' if shoot_enemy else 'в себя'}...")
    await asyncio.sleep(1.5)      

    if game_data.bullets[-1].pop() == 0:
        await Bot.send_message(chat_id=game_data.chat_id, text=f"Патрон был холостой! C игроком {player_username} все впорядке!\nКоличество оставшихся жизней: {game_data.players[player_id]['hp']}")
        await asyncio.sleep(1)
    else:
        if shoot_enemy:
            game_data.players[enemy_id]["hp"] -= 1
            await Bot.send_message(chat_id=game_data.chat_id, text=f"Патрон настоящий, и он попал прямо в {enemy_username}\nКоличество оставшихся жизней у {enemy_username}: <b>{game_data.players[enemy_id]['hp']}</b>")
            if game_data.players[enemy_id]["hp"] <= 0:
                await Bot.send_message(chat_id=game_data.chat_id, text=f"Этот день оказался последним для тебя, {enemy_username}...\nТы храбро играл, но вышел из игры проигравшим.😔\n<b>{player_username}, поздравляю тебя с победой!</b>\nКОНЕЦ ИГРЫ💯")
                #тут еще нужно добавить позже итоговую таблицу на каждого игрока: всего ходов, использованно предмтов и пр.
        else:
            game_data.players[player_id]["hp"] -= 1
            await Bot.send_message(chat_id=game_data.chat_id, text=f"Патрон настоящий, и он попал прямо в {player_username}\nКоличество оставшихся жизней у {player_username}: <b>{game_data.players[player_id]['hp']}</b>")
            if game_data.players[enemy_id]["hp"] <= 0:
                await Bot.send_message(chat_id=game_data.chat_id, text=f"Этот день оказался последним для тебя, {player_username}...\nТы храбро играл, но вышел из игры проигравшим.😔\n<b>{enemy_username}, поздравляю тебя с победой!</b>\nКОНЕЦ ИГРЫ💯")
                #тут еще нужно добавить позже итоговую таблицу на каждого игрока: всего ходов, использованно предмтов и пр.


@gameplay_router.callback_query(F.data == "")
async def shoot_enemy(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    game_data: GameSession = active_games[chat_id]

    await shoot_logic(game_data, call.from_user.id, shoot_enemy=True)

@gameplay_router.callback_query(F.data == "")
async def shoot_myself(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    game_data: GameSession = active_games[chat_id]

    await shoot_logic(game_data, call.from_user.id, shoot_enemy=False)




@gameplay_router.callback_query(F.data == "")
def use_items(self, chat_id, players: dict, bullets: list[int]):
    pass

@gameplay_router.callback_query(F.data == "")
def is_game_over(self, chat_id, players: dict) -> bool:
    pass

#дописать логигу gameplay, функции и все меню