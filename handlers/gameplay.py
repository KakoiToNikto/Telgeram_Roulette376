import asyncio
import textwrap

from aiogram import types, Router, F, Bot

from roulette_menu import before_game_menu, actions_menu, items_menu
from .session import GameSession
from .tracking import active_games
from .gamestate import GameState


gameplay_router = Router()


async def prepare_round(session: GameSession, bot: Bot):     #state=PREPARE_ROUND
    await bot.send_message(chat_id=session.chat_id, text="")
    session.state = GameState.PLAYERS_TURN

async def choose_actions(session: GameSession, bot: Bot):     #state=PLAYERS_TURN
    await bot.send_message(chat_id=session.chat_id, text="")
    
    #тут будет показываться actions_menu
    ...
    session.state = GameState.END_ROUND

async def end_round(session: GameSession, bot: Bot):     #state=END_ROUND
    await bot.send_message(chat_id=session.chat_id, text="Оба игрока походили. Подводим итоги раунда...")
    await asyncio.sleep(0.5)
    await bot.send_message(chat_id=session.chat_id, text=f"""Кол-во жизней у <b>{session.players[session.player1]['username']}: <i>{session.players[session.player1]['hp']}</i></b>\n
                           Кол-во жизней у <b>{session.players[session.player2]['username']}: <i>{session.players[session.player2]['hp']}</i></b>""")
    await bot.send_message(chat_id=session.chat_id, text=f"""Предметы у <b>{session.players[session.player1]['username']}: <i>{session.players[session.player1]['inventory']}</i></b>\n
                           Предметы у <b>{session.players[session.player2]['username']}: <i>{session.players[session.player2]['inventory']}</i></b>""")


    # session.players[session.player1]["is_handcuffed"] = False
    # session.players[session.player2]["is_handcuffed"] = False
    #мб под конец раунда делать так, чтобы наручники снимаоись обязательно

    session.state = GameState.PREPARE_ROUND

async def game_over(session: GameSession, bot: Bot) -> bool:     #state=GAME_OVER. Посмертная речь реализована сейчас в shoot, мб перенесу сюда все потом + реализовать тут итоги
    await bot.send_message(chat_id=session.chat_id, text="<b>Игра окончена</b>. Мир проигравшим, слава победившим!\nИтоги игры:...(реализовать позже)")

    #будет вызвано в случае смерти/прерывания игры. Тут подводятся итоги и все, конец, больше переключения состояния не дудет
#----------------------------------------------------------------------------------
async def shoot_logic(bot, session: GameSession, shooter_id: int, shoot_enemy: bool):
    #реализовать проверку, связанные с предметами(наручники, поджигательные снаряды и пр.) + добавить провеику текущего игрока
    enemy_id = session.player2 if shooter_id == session.player1 else session.player1
    enemy_username = (await bot.get_chat(enemy_id)).username
    player_username = (await bot.get_chat(shooter_id)).username

    if session.current_player != shooter_id:
        return
    
    await bot.send_message(chat_id=session.chat_id, text=f"Игрок {player_username} делает выстрел {'в противника' if shoot_enemy else 'в себя'}...")
    await asyncio.sleep(1.5)      

    if session.bullets.pop() == 0:
        await bot.send_message(chat_id=session.chat_id, text=f"Патрон был холостой! C игроком {player_username} все впорядке!\nКоличество оставшихся жизней: {session.players[player_id]['hp']}")
        await asyncio.sleep(1)
    else:
        session.bullets.pop()
        if shoot_enemy:
            session.players[enemy_id]["hp"] -= 1
            await bot.send_message(chat_id=session.chat_id, text=f"Патрон настоящий, и он попал прямо в {enemy_username}\nКоличество оставшихся жизней у {enemy_username}: <b>{session.players[enemy_id]['hp']}</b>")
            if session.players[enemy_id]["hp"] <= 0:
                await bot.send_message(chat_id=session.chat_id, text=f"Этот день оказался последним для тебя, {enemy_username}...\nТы храбро играл, но вышел из игры проигравшим.😔\n<b>{player_username}, поздравляю тебя с победой!</b>\nКОНЕЦ ИГРЫ💯")
                #тут еще нужно добавить позже итоговую таблицу на каждого игрока: всего ходов, использованно предмтов и пр.
        else:
            session.players[shooter_id]["hp"] -= 1
            await bot.send_message(chat_id=session.chat_id, text=f"Патрон настоящий, и он попал прямо в {player_username}\nКоличество оставшихся жизней у {player_username}: <b>{session.players[shooter_id]['hp']}</b>")
            if session.players[shooter_id]["hp"] <= 0:
                await bot.send_message(chat_id=session.chat_id, text=f"Этот день оказался последним для тебя, {player_username}...\nТы храбро играл, но вышел из игры проигравшим.😔\n<b>{enemy_username}, поздравляю тебя с победой!</b>\nКОНЕЦ ИГРЫ💯")
                #тут еще нужно добавить позже итоговую таблицу на каждого игрока: всего ходов, использованно предмтов и пр.



@gameplay_router.callback_query(F.data == "shoot_enemy")
async def shoot_enemy(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    session: GameSession = active_games[chat_id]

    await shoot_logic(call.bot, session, call.from_user.id, shoot_enemy=True)

@gameplay_router.callback_query(F.data == "shoot_myself")
async def shoot_myself(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    session: GameSession = active_games[chat_id]

    await shoot_logic(call.bot, session, call.from_user.id, shoot_enemy=False)



@gameplay_router.callback_query(F.data == "Bint")
async def use_bint(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    session: GameSession = active_games[chat_id]

    await call.answer("Бинт выбран")
    await call.message.answer(f"[Заготовка] Предмет 'Бинт' для {call.from_user.username} будет реализован позже.")


@gameplay_router.callback_query(F.data == "Magnet")
async def use_magnet(call: types.CallbackQuery, session: GameSession):
    chat_id = call.message.chat.id
    session: GameSession = active_games[chat_id]

    await call.answer("Магнит выбран")
    await call.message.answer(f"[Заготовка] Предмет 'Магнит' для {call.from_user.username} будет реализован позже.")


@gameplay_router.callback_query(F.data == "magnifying_glass")
async def use_magnifying_glass(call: types.CallbackQuery, session: GameSession):
    chat_id = call.message.chat.id
    session: GameSession = active_games[chat_id]

    await call.answer("Лупа выбран")
    await call.message.answer(f"[Заготовка] Предмет 'Лупа' для {call.from_user.username} будет реализован позже.")


@gameplay_router.callback_query(F.data == "fire_bullet")
async def use_fire_bullet(call: types.CallbackQuery, session: GameSession):
    chat_id = call.message.chat.id
    session: GameSession = active_games[chat_id]

    await call.answer("Зажигательный снаряд выбран")
    await call.message.answer(f"[Заготовка] Предмет 'Зажигательный снаряд' для {call.from_user.username} будет реализован позже.")


@gameplay_router.callback_query(F.data == "handcuffes")
async def use_handcuffes(call: types.CallbackQuery, session: GameSession):
    chat_id = call.message.chat.id
    session: GameSession = active_games[chat_id]

    await call.answer("Наручники выбраны")
    await call.message.answer(f"[Заготовка] Предмет 'Наручники' для {call.from_user.username} будет реализован позже.")


#------------------------------------------------------------------------------------
async def Game_Engine(session: GameSession, bot: Bot):
    if session.state == GameState.PREPARE_ROUND:
        await prepare_round(session, bot)
    elif session.state == GameState.PLAYERS_TURN:
        await choose_actions(session, bot)
    elif session.state == GameState.END_ROUND:
        await end_round(session, bot)
    elif session.state == GameState.GAME_OVER:
        await game_over(session, bot)
    else:
        print("Ошибка: неизвестное состояние игры.")


# реализовать функцию прерывания игры позже