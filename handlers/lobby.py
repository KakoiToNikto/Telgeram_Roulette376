import asyncio
import textwrap

from Python.TGB.Russian_Ruolette_376.roulette_menu import before_game_menu
from session import GameSession
from tracking import active_games, active_lobbies

from aiogram import types, Router
from aiogram.filters import Command, F


lobby_router = Router()


class Lobby:
    def __init__(self):
        self.players = []  #список игроков, которые вступили в игру

    # def clear(self):
    #     pass


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

        if chat_id in active_lobbies:
            await message.reply(
                "Подбор игроков уже идёт."
            )
            return

        if chat_id in active_games:
            await message.reply(
                "Игра уже запущена."
            )
            return
        
        lobby = Lobby()
        chat_id = message.chat.id

        p1 = message.from_user.id   #первый игрок - это тот, кто вызвал команду /play - сразу определили его
        lobby.players.append(p1)
        active_lobbies[chat_id] = lobby

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
    chat_id = event.message.chat.id

    if chat_id not in active_lobbies and chat_id not in active_games:
        explaning_text = "У вас нет ни активного подбора игроков, ни активной игры"
    if isinstance(event, types.Message):
            await event.reply(explaning_text)
    elif isinstance(event, types.CallbackQuery):
            await event.message.reply(explaning_text)
    if chat_id in active_lobbies:
        del active_lobbies[chat_id]
    if chat_id in active_games:
        del active_games[chat_id]


    breaking_text = f"Подбор игроков остановлен. Игрок {event.from_user.username} прервал игру"
    if isinstance(event, types.Message):
        await event.reply(breaking_text)
    elif isinstance(event, types.CallbackQuery):
        await event.message.reply(breaking_text)


@lobby_router.callback_query(F.data == "get_game")
async def get_the_game(call: types.CallbackQuery):
    chat_id = call.message.chat.id

    lobby = active_lobbies.get(chat_id)
    if lobby is None:
        await call.message.reply(
            "Активного подбора игроков нет."
        )
        return

    p2 = call.from_user.id      #второй игрок - это тот, кто нажал кнопку "Вступить в игру"
    lobby = active_lobbies[chat_id]

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

    game_session = GameSession(lobby.players, chat_id)
    active_games[chat_id] = game_session    #добавляем сессию игры в активные игры, чтобы можно было отслеживать, кто в игре
    del active_lobbies[chat_id]    #лобби нам больше не нужно, есть только игра

    await call.message.reply(f"{call.from_user.username} присоединился к игре!\n<i>Игра начинается, удачи!🤞</i>")
    await asyncio.sleep(1)
    

    #пока не уверен в системе - сессия создается только после присоединения ВТОРОГО игрока, но может быть нужно
    #будет создавать сессию сразу после вызова команды /play, чтобы можно было прерывать игру в любой момент

