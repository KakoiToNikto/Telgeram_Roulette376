import asyncio
from operator import call
from subprocess import call
from random import random
import textwrap

from aiogram import types, Router, F, Bot
from requests import session

from roulette_menu import actions_menu, items_menu
from .session import GameSession
from .tracking import active_games
from .gamestate import GameState


gameplay_router = Router()


async def prepare_round(session: GameSession, bot: Bot):     #state=PREPARE_ROUND, DONE
    session.round_number += 1

    await bot.send_message(chat_id=session.chat_id, text=f"<b>Раунд №{session.round_number}</b>{"\nВремя получить 3 особых предмета!" if session.round_number > 0 else "\n"}")
    if session.round_number > 0:
        await distribute_items(session, bot)     #оба игрока получают по 3 случайных предмета
        session.next_turn()     #первый ходит тот, кто не ходил в прошлом раунде. В первом раунде ходит случайный игрок, определенный в GameSession

    await asyncio.sleep(1)
    await bot.send_message(chat_id=session.chat_id, text=f"Игрок {session.players[session.current_player]['username']} начинает первым.\nУдачи!🤞")
            
    session.state = GameState.PLAYERS_TURN


async def choose_actions(session: GameSession, bot: Bot):     #state=PLAYERS_TURN, DONE
    await bot.send_message(chat_id=session.chat_id, text="Выбери действия для этого раунда(<i>помни, что после выстрела в противника твой ход окончен</i>):", reply_markup=actions_menu())

    session.state = GameState.END_ROUND


async def end_round(session: GameSession, bot: Bot):     #state=END_ROUND, DONE
    await bot.send_message(chat_id=session.chat_id, text="Оба игрока походили. Подводим итоги раунда...")
    await asyncio.sleep(0.5)
    await bot.send_message(chat_id=session.chat_id, text=f"""Кол-во жизней у <b>{session.players[session.player1]['username']}: <i>{session.players[session.player1]['hp']}</i></b>\n
                           Кол-во жизней у <b>{session.players[session.player2]['username']}: <i>{session.players[session.player2]['hp']}</i></b>""")
    await bot.send_message(chat_id=session.chat_id, text=f"""Предметы у <b>{session.players[session.player1]['username']}: <i>{session.players[session.player1]['inventory']}</i></b>\n
                           Предметы у <b>{session.players[session.player2]['username']}: <i>{session.players[session.player2]['inventory']}</i></b>""")
    await asyncio.sleep(1.5)
    await bot.send_message(text="Игра все инетереснее, мы продолжаем!👾")

    # session.players[session.player1]["is_handcuffed"] = False
    # session.players[session.player2]["is_handcuffed"] = False
    #мб под конец раунда делать так, чтобы наручники снимаоись обязательно

    session.state = GameState.PREPARE_ROUND


async def game_over(session: GameSession, bot: Bot) -> bool:     #state=GAME_OVER. Посмертная речь реализована сейчас в shoot, мб перенесу сюда все потом + реализовать тут итоги
    await bot.send_message(chat_id=session.chat_id, text="<b>Игра окончена</b>. Мир проигравшим, слава победившим!\nИтоги игры:...(реализовать позже)")

    #будет вызвано в случае смерти/прерывания игры. Тут подводятся итоги и все, конец, больше переключения состояния не дудет

#----------------------------------------------------------------------------------
async def distribute_items(session: GameSession, bot: Bot):
    items = ["Бинт", "Магнит", "Лупа", "Зажигательный снаряд", "Наручники"]

    for player_id in session.players:
        player = session.players[player_id]
        if player["inventory"].__len__() >= 9:
            await bot.send_message(chat_id=session.chat_id, text=f"Игрок {player['username']} уже имеет 9 предметов, поэтому не может получить новые предметы.")
            continue

        for _ in range(3):
            item = random.choice(items)
            player["inventory"].append(item)
            await bot.send_message(chat_id=session.chat_id, text=f"Игрок {player['username']} получил предмет: {item}")
            await asyncio.sleep(0.5)

        await asyncio.sleep(0.7)
        await bot.send_message(chat_id=session.chat_id, text=f"------")
        await asyncio.sleep(0.7) 


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



@gameplay_router.callback_query(F.data == "use_items")
async def use_items(call: types.CallbackQuery, session: GameSession):
    if call.from_user.id != session.current_player:
        await call.answer("Сейчас не твой ход. Жди")
        return
    
    await call.answer("Выбери предмет(-ы) для использования")
    await call.message.reply("Выбери предмет(-ы) для использования", reply_markup=items_menu(
        bint_count=session.players[call.from_user.id]["inventory"].count("Бинт"),
        magnet_count=session.players[call.from_user.id]["inventory"].count("Магнит"),
        magnifying_glass_count=session.players[call.from_user.id]["inventory"].count("Лупа"),
        fire_bullet_count=session.players[call.from_user.id]["inventory"].count("Зажигательный снаряд"),
        handcuffes_count=session.players[call.from_user.id]["inventory"].count("Наручники")
        )
    )



@gameplay_router.callback_query(F.data == "Bint")   #DONE
async def use_bint(call: types.CallbackQuery, session: GameSession):
    if call.from_user.id != session.current_player:
        await call.answer("Сейчас не твой ход. Жди")
        return
    
    if session.players[call.from_user.id]["inventory"].count("Бинт") == 0:
        await call.answer("У тебя нет бинта!")
        return

    chat_id = call.message.chat.id
    session: GameSession = active_games[chat_id]

    await call.answer("Бинт выбран")
    if session.players[call.from_user.id]["hp"] >= 6:
        await call.message.reply("У тебя уже максимальное количество жизней - 6. Ты не можешь использовать бинт")
        return
    
    session.players[call.from_user.id]["hp"] += 1
    session.players[call.from_user.id]["inventory"].remove("Бинт")
    await call.message.reply(f"{call.from_user.username} использовал бинт и восстановил 1 жизнь.\nТеперь у {call.from_user.username} <b>{session.players[call.from_user.id]['hp']}</b> жизней")

    await call.message.reply("Выбери предмет(-ы) для использования", reply_markup=items_menu(
        bint_count=session.players[call.from_user.id]["inventory"].count("Бинт"),
        magnet_count=session.players[call.from_user.id]["inventory"].count("Магнит"),
        magnifying_glass_count=session.players[call.from_user.id]["inventory"].count("Лупа"),
        fire_bullet_count=session.players[call.from_user.id]["inventory"].count("Зажигательный снаряд"),
        handcuffes_count=session.players[call.from_user.id]["inventory"].count("Наручники")
        )
    )


@gameplay_router.callback_query(F.data == "Magnet")     #DONE
async def use_magnet(call: types.CallbackQuery, session: GameSession):
    if call.from_user.id != session.current_player:
        await call.answer("Сейчас не твой ход. Жди")
        return

    if session.players[call.from_user.id]["inventory"].count("Магнит") == 0:
        await call.answer("У тебя нет магнита!")
        return

    chat_id = call.message.chat.id
    session: GameSession = active_games[chat_id]

    await call.answer("Магнит выбран")
    if session.bullets.__len__() == 0:
        await call.message.reply("В револьвере уже нет патронов, поэтому магнит не сработает.")
        return
    
    session.players[call.from_user.id]["inventory"].remove("Магнит")
    await call.message.answer(f"Магнит приставлен к револьверу... Патрон почти вынут...")
    await asyncio.sleep(0.5)
    await call.message.answer(f"Патрон вынут из револьвера! Теперь в револьвере <b>{session.bullets.__len__()}</b> патронов.\nТы вынул <b>{'Боевой патрон' if session.bullets.pop() == 1 else 'холостой патрон'}</b>")
    
    await call.message.reply("Выбери предмет(-ы) для использования", reply_markup=items_menu(
        bint_count=session.players[call.from_user.id]["inventory"].count("Бинт"),
        magnet_count=session.players[call.from_user.id]["inventory"].count("Магнит"),
        magnifying_glass_count=session.players[call.from_user.id]["inventory"].count("Лупа"),
        fire_bullet_count=session.players[call.from_user.id]["inventory"].count("Зажигательный снаряд"),
        handcuffes_count=session.players[call.from_user.id]["inventory"].count("Наручники")
        )
    )


@gameplay_router.callback_query(F.data == "magnifying_glass")   #DONE
async def use_magnifying_glass(call: types.CallbackQuery, session: GameSession):
    if call.from_user.id != session.current_player:
        await call.answer("Сейчас не твой ход. Жди")
        return

    if session.players[call.from_user.id]["inventory"].count("Лупа") == 0:
        await call.answer("У тебя нет лупы!")
        return

    chat_id = call.message.chat.id
    session: GameSession = active_games[chat_id]
    
    await call.answer("Лупа выбрана")
    if session.bullets.__len__() == 0:
        await call.message.reply("В револьвере уже нет патронов, поэтому лупа не сработает.")
        return
    
    session.players[call.from_user.id]["inventory"].remove("Лупа")
    await call.message.answer(f"Лупа приставлена к револьверу... Патрон уже виден...")
    await asyncio.sleep(0.5)
    await call.message.answer(f"Ты разглядел патрон!\nЭто <b>{'Боевой патрон' if session.bullets.pop() == 1 else 'холостой патрон'}</b>")
    
    await call.message.reply("Выбери предмет(-ы) для использования", reply_markup=items_menu(
        bint_count=session.players[call.from_user.id]["inventory"].count("Бинт"),
        magnet_count=session.players[call.from_user.id]["inventory"].count("Магнит"),
        magnifying_glass_count=session.players[call.from_user.id]["inventory"].count("Лупа"),
        fire_bullet_count=session.players[call.from_user.id]["inventory"].count("Зажигательный снаряд"),
        handcuffes_count=session.players[call.from_user.id]["inventory"].count("Наручники")
        )
    )


@gameplay_router.callback_query(F.data == "fire_bullet")
async def use_fire_bullet(call: types.CallbackQuery, session: GameSession):
    if call.from_user.id != session.current_player:
        await call.answer("Сейчас не твой ход. Жди")
        return

    if session.players[call.from_user.id]["inventory"].count("Зажигательный снаряд") == 0:
        await call.answer("У тебя нет зажигательного снаряда!")
        return

    chat_id = call.message.chat.id
    session: GameSession = active_games[chat_id]

    await call.answer("Зажигательный снаряд выбран")
    await call.message.answer(f"[Заготовка] Предмет 'Зажигательный снаряд' для {call.from_user.username} будет реализован позже.")


@gameplay_router.callback_query(F.data == "handcuffes")
async def use_handcuffes(call: types.CallbackQuery, session: GameSession):
    if call.from_user.id != session.current_player:
        await call.answer("Сейчас не твой ход. Жди")
        return
    
    if session.players[call.from_user.id]["inventory"].count("Наручники") == 0:
        await call.answer("У тебя нет наручников!")
        return

    chat_id = call.message.chat.id
    session: GameSession = active_games[chat_id]

    await call.answer("Наручники выбраны")
    await call.message.answer(f"[Заготовка] Предмет 'Наручники' для {call.from_user.username} будет реализован позже.")


@gameplay_router.callback_query(F.data == "back_gameplay")      #DONE
async def back_gameplay(call: types.CallbackQuery, session: GameSession):
    if call.from_user.id != session.current_player:
        await call.answer("Сейчас не твой ход. Жди")
        return
    
    await call.answer("Возврат в меню действий")
    await call.message.reply("Выбери предмет(-ы) для использования", reply_markup=items_menu(
        bint_count=session.players[call.from_user.id]["inventory"].count("Бинт"),
        magnet_count=session.players[call.from_user.id]["inventory"].count("Магнит"),
        magnifying_glass_count=session.players[call.from_user.id]["inventory"].count("Лупа"),
        fire_bullet_count=session.players[call.from_user.id]["inventory"].count("Зажигательный снаряд"),
        handcuffes_count=session.players[call.from_user.id]["inventory"].count("Наручники")
        )
    )

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