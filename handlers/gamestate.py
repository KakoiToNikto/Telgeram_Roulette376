from enum import Enum, auto     #для состояний игры(какая стадия игры и пр.)

class GameState(Enum):
    PREPARE_ROUND = auto()
    PLAYERS_TURN = auto()
    END_ROUND = auto()
    GAME_OVER = auto()  
