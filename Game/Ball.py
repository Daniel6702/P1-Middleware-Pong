import pygame
from properties import *
from random import randint
from Game.Paddle import Paddle
from typing import Callable

class Ball(pygame.Rect):
    def __init__(
        self,
        x=WIDTH // 2 - BALL_SIZE // 2,
        y=HEIGHT // 2 - BALL_SIZE // 2,
        width=BALL_SIZE,
        height=BALL_SIZE,
        speed_x=BALL_SPEED_X,
        speed_y=BALL_SPEED_Y,
        color=WHITE,
        add_score: Callable = None,
        skip_reset: bool = False  # New parameter
    ):
        super().__init__(x, y, width, height)
        self.add_score = add_score
        self.color = color
        self.speed_x = speed_x
        self.speed_y = speed_y
        if not skip_reset:
            self.reset()

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

    def collision_ceiling(self):
        if self.y <= 0 or self.y + self.height >= HEIGHT:
            self.speed_y *= -1

    def collision_paddle(self, paddle: 'Paddle'):
        if self.colliderect(paddle):
            self.speed_x *= -1

    def reset(self):
        self.x = WIDTH // 2 - BALL_SIZE // 2
        self.y = HEIGHT // 2 - BALL_SIZE // 2
        self.speed_x = BALL_SPEED_X if self.speed_x < 0 else -BALL_SPEED_X
        self.speed_y = BALL_SPEED_Y if self.speed_y < 0 else -BALL_SPEED_Y

    def update(self, paddles: list):
        self.move()
        self.collision_ceiling()
        for paddle in paddles:
            self.collision_paddle(paddle)
        if self.x <= 0:
            self.reset()
            if self.add_score:
                self.add_score(1)  # Opponent scores
        if self.x + self.width >= WIDTH:
            self.reset()
            if self.add_score:
                self.add_score(0)  # Player scores

    def update_from_dict(self, data: dict):
        self.x = data['x']
        self.y = data['y']
        self.width = data['width']
        self.height = data['height']
        self.speed_x = data['speed_x']
        self.speed_y = data['speed_y']
        self.color = tuple(data['color'])

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self)

    @staticmethod
    def from_dict(data: dict) -> 'Ball':
        return Ball(
            x=data['x'],
            y=data['y'],
            width=data['width'],
            height=data['height'],
            speed_x=data['speed_x'],
            speed_y=data['speed_y'],
            color=tuple(data['color']),
            skip_reset=True  # Prevent resetting position
        )

    def to_dict(self) -> dict:
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'speed_x': self.speed_x,
            'speed_y': self.speed_y,
            'color': list(self.color)  # Convert tuple to list for JSON serialization
        }