import pygame
from game_properties import *
from random import randint

class Paddle(pygame.Rect):
    def __init__(self, x, y, width=PADDLE_WIDTH, height=PADDLE_HEIGHT,
                 speed=PADDLE_SPEED, color=WHITE):
        super().__init__(x, y, width, height)
        self.speed = speed
        self.color = (randint(100, 255), randint(100, 255), randint(100, 255))
        self.reset()

    def move(self, direction):
        if direction == "up" and self.top > 0:
            self.y -= self.speed
        if direction == "down" and self.bottom < HEIGHT:
            self.y += self.speed

    def reset(self):
        self.y = (HEIGHT - PADDLE_HEIGHT) // 2

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self)

    def to_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'speed': self.speed,
            'color': list(self.color)  # Convert tuple to list for JSON serialization
        }