import pygame
from Components.game_properties import *

##################################
# Paddle
##################################
class Paddle(pygame.Rect):
    def __init__(self, x, y, width = PADDLE_WIDTH, height = PADDLE_HEIGHT, speed = PADDLE_SPEED, color = WHITE):
        super().__init__(x, y, width, height)
        self.speed = speed
        self.color = color
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

##################################
# Ball
##################################
class Ball(pygame.Rect):
    def __init__(self, x = WIDTH // 2 - BALL_SIZE // 2, y = HEIGHT // 2 - BALL_SIZE // 2, size = BALL_SIZE, speed_x = BALL_SPEED_X, speed_y = BALL_SPEED_Y, color = WHITE):
        super().__init__(x, y, size, size)
        self.color = color
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.reset()

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

    def collision_ceiling(self):
        if self.y <= 0 or self.y >= HEIGHT:
            self.speed_y *= -1

    def collision_paddle(self, paddle):
        if self.colliderect(paddle):
            self.speed_x *= -1

    def reset(self):
        self.x = WIDTH // 2 - BALL_SIZE // 2
        self.y = HEIGHT // 2 - BALL_SIZE // 2
        self.speed_x *= -1
        self.speed_y *= -1

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self)

    def update(self, padles):
        self.move()
        self.collision_ceiling()
        for paddle in padles:
            self.collision_paddle(paddle)
        if self.x <= 0 or self.x >= WIDTH:
            self.reset()
