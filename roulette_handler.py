import textwrap
import asyncio

from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command, or_f

from roulette_menu import roulette_menu_ruler, get_back_menu,  before_game_menu
#from roulette_db import user_stats, global_stats

roulette_handler_router = Router()

@roulette_handler_router.message(Command('creator'))
async def creatorer(message: types.Message):
    await message.reply("<u>Создатель этого бота - @kakoi_to_nikto !</u>")


@roulette_handler_router.message(or_f(Command("start"), CommandStart()))
async def starter(message: types.Message):
    await message.reply(
        textwrap.dedent(
            """
            💥Приветствую тебя в боте Русская Рулетка 376!☠️
            Я могу помочь тебе сыграть в эту игру,
            а также показать статистику и правила. Выбери ниже, что ты хочешь сделать:
            """
        ).strip(),
        reply_markup=roulette_menu_ruler(),
    )

#-------------------------------------
#Обработчик меню
@roulette_handler_router.callback_query(F.data == "back")
async def back(call: types.CallbackQuery):
    await call.message.edit_text(
        textwrap.dedent(
            """
            💥Приветствую тебя в боте Русская Рулетка 376!☠️
            Я могу помочь тебе сыграть в эту игру,
            а также показать статистику и правила. Выбери ниже, что ты хочешь сделать:
            """
        ).strip(),
        reply_markup=roulette_menu_ruler(),
    )


@roulette_handler_router.callback_query(F.data == "play")
async def play(call: types.CallbackQuery):
    await call.message.edit_text(
        textwrap.dedent(
            """
            Выживет только один... Ты уверен?

            Чтобы начать игру, напиши команду /play в группе с другими игроками.
            Чтобы вернуться в меню, нажми кнопку ниже.
            """
        ).strip(),
        reply_markup=get_back_menu(),
    )


@roulette_handler_router.callback_query(F.data == "stats")
async def stats(call: types.CallbackQuery):
    await call.message.edit_text(
        textwrap.dedent(
            """
            Твоя статистика:

            Выигрыши: (взять из БД)
            Всего игр: (взять из БД)
            Процент побед: (вычислить)

            Чтобы вернуться в меню, нажми кнопку ниже.
            """
        ).strip(),
        reply_markup=get_back_menu(),
    )

@roulette_handler_router.callback_query(F.data == "rules")
async def rules(call: types.CallbackQuery):
    await call.message.edit_text(
        textwrap.dedent(
            """
            <b>Перед игрой</b>:
            Меня нужно добавить в группу с другим игроком(-ами).
            Игра начнется после команды /play в группе, когда второй игрок подтвердит участие.

            <b>Правила игры - Русской Рулетки 376:</b>
            У каждого из игроков есть 5 жизней. В начале каждого раунда один из игроков случайным
            образом получает револьвер с 6-ю камерами. Также рандомно определяется, сколько холостых
            и боевых патрон будет в револьвере. В начале раунда я напишу, сколько боевых/холостых патрон,
            но они рандомно кладутся в револьвер.
            Игрок, получивший револьвер, может выбрать, выстрелить ли себе в голову или выстрелить в другого игрока.

            <i>• Если игрок стреляет в себя, а в револьвере был боевой патрон, он теряет жизнь.
            • Если игрок стреляет в себя, а в револьвере был холостой патрон, ничего не происходит и игрок продолжает стрелять.

            • Если игрок стреляет в другого игрока, а в револьвере был боевой патрон, другой игрок теряет жизнь и ему передается револьвер.
            • Если игрок стреляет в другого игрока, а в револьвере был холостой патрон, с другим игроком ничего не происходит и ему передается револьвер.</i>

            Игра продолжается, пока у одного из игроков не останется жизней. Этот игрок считается проигравшим,
            а другой игрок — победителем.

            <b>НО!</b> После первого раунда все игроки могут получить <b>особые предметы</b>, которые могут изменить ход игры.
            Игрокам будет даваться рандомно 5 предметов, описанных ниже.
            Предметы можно использовать в любой момент во время своего хода.

            <i>• <b>Бинт🤕</b>: игрок может восстановить одну жизнь.
            • <b>Магнит🧲</b>: игрок может достать и выкинуть следующий патрон из револьвера.
            • <b>Лупа👁️</b>: игрок может увидеть, какой патрон будет следующим.
            • <b>Поджигательный снаряд🔥</b>: игрок может положить его в револьвер. Если следующий патрон боевой, револьвер нанесет 2 урона вместо 1. Если холостой — ничего не произойдет.
            • <b>Наручники⛓️</b>: игрок может надеть наручники на другого игрока. Этот игрок пропускает свой следующий ход (револьвер ему не передается).</i>
            """
        ).strip(),
        reply_markup=get_back_menu(),
    )

#• <b>Инвеhтор</b>: игрок может использовать инветор, чтобы поменять текущий патрон на противоположный(боевой на холостой и наоборот).


#--------------------------------
#Запуск игры

@roulette_handler_router.callback_query(F.data == "get_game")
async def get_the_game(call: types.CallbackQuery):
    call.message.reply(f"{call.from_user.username} присоединился к игре!\n<i>Игра начинается, удачи!🤞</i>")
    await asyncio.sleep(1)    #ждет 1 секунду
    # Дальше здесь часть гемплея - отправляется гифка, художественное сообщение и начинается игра:
    #  рассчет патрон и выбор первого стрелющего. Это можно сделать в отдельном роутере

@roulette_handler_router.callback_query(F.data == "break_game")
@roulette_handler_router.message(F.text.lower().contains("стоп"))
async def stop_matchmaking(call: types.CallbackQuery):
    await call.message.reply(f"Подбор игроков/игра остановлена. Чтобы снова начать подбор игроков в игру, напиши команду /play !")
    #тут написать функцию прерывания сессии подбора игроков
    # (в БД кладется что игрок сыграл игру только после окончания игры)


@roulette_handler_router.message(Command("play"))
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

#Тут разобраться и написать функцию, которая будет запускаться после команды play
# - делает сессию и ожидает набора 2-х разных юзеров. После набора начинает игру
# (дальше идут геймплейные функции)

#Еще 1 задача: разделить этот файл на роутеры и файлы по задачам

