import pygame
from properties import *
from random import randint

class Paddle(pygame.Rect):
    def __init__(self, x, y, width=PADDLE_WIDTH, height=PADDLE_HEIGHT,
                 speed=PADDLE_SPEED, color=(randint(100, 255), randint(100, 255), randint(100, 255))):
        super().__init__(x, y, width, height)
        self.speed = speed
        self.color = color

    def move(self, direction: str):
        if direction == "up" and self.top > 0:
            self.y -= self.speed
        if direction == "down" and self.bottom < HEIGHT:
            self.y += self.speed

    def update_from_dict(self, data: dict):
        self.x = data['x']
        self.y = data['y']
        self.width = data['width']
        self.height = data['height']
        self.speed = data['speed']
        self.color = tuple(data['color'])

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
    
    def from_dict(data: dict) -> 'Paddle':
        return Paddle(data['x'], data['y'], data['width'], data['height'], data['speed'], tuple(data['color']))