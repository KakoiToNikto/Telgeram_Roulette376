from random import choice, random
from lobby import lobby


async def bullets_position(real, fake):
    bullets = [1] * real + [0] * fake
    random.shuffle(bullets)
    return bullets

hp = 5

class GameSession:
    def __init__(self, player_ids: list[int], chat_id: int):
        """
        player_ids: список из двух ID игроков (из lobby.players)
        chat_id: ID чата (для логирования или БД)
        """
        p1_id, p2_id = player_ids[0], player_ids[1]
        
        self.players = {
            p1_id: {
                "id": p1_id,
                "hp": hp,
                "is_alive": True,
                "is_handcuffed": False,
                "inventory": []
            },
            p2_id: {
                "id": p2_id,
                "hp": hp,
                "is_alive": True,
                "is_handcuffed": False, 
                "inventory": []
            }
        }
        
        self.chat_id = chat_id

        real_bullets = random.choice([5, 4, 4, 3, 3, 2, 2, 1])   #рандомно определяем, сколько боевых патрон будет в револьвере
        fake_bullets = 6 - real_bullets     #остальные патроны - холостые
        self.bullet_position = bullets_position(real_bullets, fake_bullets)   

        self.current_player = choice([p1_id, p2_id])      #в начале игры рандомно определили первого игрока