#В это файле будет сессия подбора игроков после вызова команды /play в группе

import asyncio
import textwrap
from Python.TGB.Russian_Ruolette_376.roulette_menu import before_game_menu

from aiogram import types, Router
from aiogram.filters import Command, F

lobby_router = Router()

@lobby_router.message(Command("play"))
async def matchmaking(message: types.Message):
    if message.chat.type == types.ChatType.PRIVATE:
        await message.reply(
            textwrap.dedent(
            """
            Чтобы начать игру, тебе нужно добавить меня в группу с другим игроком(-ами).
            Игра начнется после команды /play в группе, когда второй игрок подтвердит участие.
            """
            ).strip()
        )
        return False   #отдается False, если команда play была вызвана в личке, и подбор игроков не начинается
    else: #(messgae.chat.type == types.ChatType.GROUP or message.chat.type == types.ChatType.SUPERGROUP)
        await message.reply(
            textwrap.dedent(
                """
                <b>ПОДБОР ИГРОКОВ. <i>ВОЙДУТ ДВОЕ, ВЫЙДЕТ ТОЛЬКО ОДИН</i></b>
                Как только второй игрок войдет в эту игру, ваша дуэль на смерть начнется!
                """
            ).strip(),
            reply_markup=before_game_menu()
        )
        return True    #отдается True, если компанда play была вызвана в группе, и начинается подбор игроков


@lobby_router.callback_query(F.data == "break_game")
@lobby_router.message(F.text.lower().contains("стоп"))
async def stop_matchmaking(call: types.CallbackQuery):
    await call.message.reply(f"Подбор игроков/игра остановлена. Чтобы снова начать подбор игроков в игру, напиши команду /play !")
    #тут написать функцию прерывания сессии подбора игроков
    # (в БД кладется что игрок сыграл игру только после окончания игры)


@lobby_router.callback_query(F.data == "get_game")
async def get_the_game(call: types.CallbackQuery):
    await call.message.reply(f"{call.from_user.username} присоединился к игре!\n<i>Игра начинается, удачи!🤞</i>")
    await asyncio.sleep(1)    #ждет 1 секунду
    # Дальше здесь часть гемплея - отправляется гифка, художественное сообщение и начинается игра:
    #  рассчет патрон и выбор первого стрелющего. Это можно сделать в отдельном роутере
