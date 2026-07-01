import random

from gamestate import GameState

def bullets_position(real, fake):
    bullets = [1] * real + [0] * fake
    random.shuffle(bullets)
    return bullets


class GameSession:
    def __init__(self, player_ids: list[int], players_names: list[str], chat_id: int):
        """
        player_ids: список из двух ID игроков (из lobby.players)
        chat_id: ID чата (для логгирования или БД)
        """
        p1_id, p2_id = player_ids
        p1_name, p2_name = players_names
        self.HP = 5

        self.players = {
            p1_id: {
                "id": p1_id,
                "username": p1_name,
                "hp": self.HP,
                "is_alive": True,
                "is_handcuffed": False,
                "inventory": []
            },
            p2_id: {
                "id": p2_id,
                "username": p2_name,
                "hp": self.HP,
                "is_alive": True,
                "is_handcuffed": False, 
                "inventory": []
            }
        }
        
        self.chat_id = chat_id

        real_bullets = random.choice([5, 4, 4, 3, 3, 2, 2, 1])   #рандомно определяем, сколько боевых патрон будет в револьвере
        fake_bullets = 6 - real_bullets     #остальные патроны - холостые
        self.bullets = bullets_position(real_bullets, fake_bullets)   

        self.current_player = random.choice([p1_id, p2_id])      #в начале игры рандомно определили первого игрока

        self.player1 = p1_id    #для более приятной читаемости
        self.player2 = p2_id

        self.state = GameState.PREPARE_ROUND   #начальное состояние игры - подготовка к раунду, потом в функциях меняем и обновляем в движке gameplay.py
        
    def next_turn(self):       #на будущее, в gameplay пригодится
        if self.current_player == self.player1:
            self.current_player = self.player2
        else:
            self.current_player = self.player1

# #локальный тест
# session = GameSession([11111, 22222], 376)
# print(session.players, session.player1, session.player2, session.current_player, session.players[session.current_player]["is_alive"], sep="\n")

