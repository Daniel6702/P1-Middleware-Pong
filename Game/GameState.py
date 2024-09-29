from dataclasses import dataclass
import json
from Game.Paddle import Paddle
from Game.Ball import Ball

@dataclass
class GameState:
    paddle: 'Paddle'
    ball: 'Ball' = None  # Ball can be None for non-owners
    score: list = None

    def to_dict(self) -> dict:
        """
        Convert the GameState to a dictionary.
        """
        data = {
            'paddle': self.paddle.to_dict(),
        }
        if self.ball is not None:
            data['ball'] = self.ball.to_dict()
            data['score'] = self.score
        return data

    def to_json(self) -> str:
        """
        Serialize the GameState to a JSON string.
        """
        return json.dumps(self.to_dict())

    @staticmethod
    def from_dict(data: dict) -> 'GameState':
        """
        Create a GameState instance from a dictionary.
        """
        paddle = Paddle.from_dict(data['paddle'])
        ball = Ball.from_dict(data['ball']) if 'ball' in data else None
        score = data.get('score', None)
        return GameState(paddle=paddle, ball=ball, score=score)