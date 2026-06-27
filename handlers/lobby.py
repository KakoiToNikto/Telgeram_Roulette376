import asyncio
import textwrap

from roulette_menu import before_game_menu
from .session import GameSession
from .tracking import active_games, active_lobbies

from aiogram import types, Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command


lobby_router = Router()


class Lobby:
    def __init__(self) -> None:
        self.players = []  #список игроков, которые вступили в игру


@lobby_router.callback_query(F.data == "break_game")
@lobby_router.message(F.text.lower().contains("стоп"))
@lobby_router.message(Command("break_game"))
async def stop_matchmaking(event):      # event может быть CallbackQuery или Message
    chat_id = event.message.chat.id

    if chat_id not in active_lobbies and chat_id not in active_games:
        explaning_text = "У вас нет ни активного подбора игроков, ни активной игры"
        if isinstance(event, types.Message):
                await event.edit_text(explaning_text)
        elif isinstance(event, types.CallbackQuery):
                await event.answer(explaning_text)
    if chat_id in active_lobbies:
        del active_lobbies[chat_id]
    if chat_id in active_games:
        del active_games[chat_id]


    breaking_text = f"Подбор игроков остановлен. Игрок {event.from_user.username} прервал игру"
    if isinstance(event, types.Message):
        await event.edit_text(breaking_text)
    elif isinstance(event, types.CallbackQuery):
        await event.message.edit_text(breaking_text)
        await event.answer("Подбор игроков остановлен")   #чтобы inline кнопка считала ответ, нужен обязаиельно answer

#----------------------------------------------------

@lobby_router.message(Command("play"))
async def matchmaking(message: types.Message):
    if message.chat.type == ChatType.GROUP or message.chat.type == ChatType.SUPERGROUP:
        await message.reply(
            textwrap.dedent(
                """
                <b>ПОДБОР ИГРОКОВ. <i>ВОЙДУТ ДВОЕ, ВЫЙДЕТ ТОЛЬКО ОДИН</i></b>
                Как только второй игрок войдет в эту игру, ваша дуэль на смерть начнется!
                """
            ).strip(),
            reply_markup=before_game_menu()
        )

        chat_id = message.chat.id

        if chat_id in active_lobbies:
            await message.reply(
                "Подбор игроков уже идёт."
            )
            return

        if chat_id in active_games:
            await message.reply(
                f"<i>{message.from_user.username}, игра в этой группе уже идет.\nДождитесь окончания игры или сыграйте в другой группе</i>"
            )
            return
        
        lobby = Lobby()

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

@lobby_router.callback_query(F.data == "get_game")
async def get_the_game(call: types.CallbackQuery):
    chat_id = call.message.chat.id

    lobby = active_lobbies.get(chat_id)
    if lobby is None:
        await call.answer(
            "Активного подбора игроков нет."
        )
        return

    p2 = call.from_user.id      #второй игрок - это тот, кто нажал кнопку "Вступить в игру"
    lobby = active_lobbies[chat_id]

    if p2 == lobby.players[0]:      #если второй игрок - это тот же, кто вызвал команду /play, то он не может вступить в игру
        await call.answer("Ты уже в игре! Жди второго игрока...")
        return

    if len(lobby.players) >= 2:     #если в игре уже есть два игрока, то третий не может вступить в игру
        await call.answer("В этой игре уже есть два игрока! Подожди, пока начнется новая игра...")
        return
    if len(lobby.players) == 0:     #если в игре нет игроков, то второй игрок не может вступить в игру
        await call.answer("Пока нет игроков, которые начали игру! Напиши команду /play в группе, чтобы начать игру!")
        return
    
    lobby.players.append(p2)    #добавляем второго игрока в список игроков

    game_session = GameSession(lobby.players, chat_id)
    active_games[chat_id] = game_session    #добавляем сессию игры в активные игры, чтобы можно было отслеживать, кто в игре
    del active_lobbies[chat_id]    #лобби нам больше не нужно, есть только игра

    await call.answer()     #чтобы inline кнопка считала ответ, нужен обязаиельно answer
    await call.message.edit_text(f"{call.from_user.username} присоединился к игре!\n<b>Игра начинается. {(call.bot.get_chat(lobby.players[0])).username} и {(call.bot.get_chat(lobby.players[1])).username}, удачи!🤞</b>")
    await asyncio.sleep(1)


