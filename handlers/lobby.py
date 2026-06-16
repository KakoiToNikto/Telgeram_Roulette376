#В это файле будет сессия подбора игроков после вызова команды /play в группе

import asyncio
import textwrap
from Python.TGB.Russian_Ruolette_376.roulette_menu import before_game_menu
from session import GameSession

from aiogram import types, Router
from aiogram.filters import Command, F


lobby_router = Router()


class Lobby:
    def __init__(self):
        self.players = []  #список игроков, которые вступили в игру

lobby = Lobby()


@lobby_router.message(Command("play"))
async def matchmaking(message: types.Message):
    if message.chat.type == types.ChatType.GROUP or message.chat.type == types.ChatType.SUPERGROUP:
        await message.reply(
            textwrap.dedent(
                """
                <b>ПОДБОР ИГРОКОВ. <i>ВОЙДУТ ДВОЕ, ВЫЙДЕТ ТОЛЬКО ОДИН</i></b>
                Как только второй игрок войдет в эту игру, ваша дуэль на смерть начнется!
                """
            ).strip(),
            reply_markup=before_game_menu()
        )

        lobby.clear()   #очищаем список игроков, чтобы не было проблем с предыдущими играми

        p1 = message.from_user.id   #первый игрок - это тот, кто вызвал команду /play - сразу определили его
        lobby.players.append(p1)

    else:   #(messgae.chat.type == types.ChatType.PRIVATE)
         await message.reply(
            textwrap.dedent(
            """
            Чтобы начать игру, тебе нужно добавить меня в группу с другим игроком(-ами).
            Игра начнется после команды /play в группе, когда второй игрок подтвердит участие.
            """
            ).strip()
        )

#----------------------------------------------------

@lobby_router.callback_query(F.data == "break_game")
@lobby_router.message(F.text.lower().contains("стоп"))
@lobby_router.message(Command("break_game"))
async def stop_matchmaking(event):      # event может быть CallbackQuery или Message
    # try:
    #     message_obj = event.message
    # except Exception:
    #     message_obj = event     #calback_query не имеет атрибута message, поэтому в случае ошибки при попытке доступа к нему, мы просто используем сам объект события (который является Message) для получения chat_id и отправки ответа пользователю.

    # chat_id = message_obj.chat.id
    # # останавливаем лобби для этого чата, если есть
    # if lobby and lobby.players and lobby.players[0] and chat_id == message_obj.chat.id:
    #     lobby.stop()

    # await message_obj.reply("Подбор игроков/игра остановлена. Чтобы снова начать подбор игроков в игру, напиши команду /play !")
    #тут написать функцию прерывания сессии подбора игроков
    #(в БД кладется что игрок сыграл игру только после окончания игры)
    pass

@lobby_router.callback_query(F.data == "get_game")
async def get_the_game(call: types.CallbackQuery):
    p2 = call.from_user.id      #второй игрок - это тот, кто нажал кнопку "Вступить в игру"

    if p2 == lobby.players[0]:      #если второй игрок - это тот же, кто вызвал команду /play, то он не может вступить в игру
        await call.message.reply("Ты уже в игре! Жди второго игрока...")
        return

    if len(lobby.players) >= 2:     #если в игре уже есть два игрока, то третий не может вступить в игру
        await call.message.reply("В этой игре уже есть два игрока! Подожди, пока начнется новая игра...")
        return
    if len(lobby.players) == 0:     #если в игре нет игроков, то второй игрок не может вступить в игру
        await call.message.reply("Пока нет игроков, которые начали игру! Напиши команду /play в группе, чтобы начать игру!")
        return
    
    lobby.players.append(p2)    #добавляем второго игрока в список игроков
    
    await call.message.reply(f"{call.from_user.username} присоединился к игре!\n<i>Игра начинается, удачи!🤞</i>")
    await asyncio.sleep(1)
    
    game_session = GameSession(lobby.players, call.message.chat.id)
    
    # Здесь можно добавить логику старта игры, например:
    # await start_game(call.message, game_session)
