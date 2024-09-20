import pygame
from random import randint
from assets import Ball, Paddle
from game_properties import *
from services import *

if __name__ == "__main__":
    # Initialize Pygame
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong")

    # Create paddles and ball
    left_paddle = Paddle(x=10, y=(HEIGHT - PADDLE_HEIGHT) // 2)
    right_paddle = Paddle(x=WIDTH - 20, y=(HEIGHT - PADDLE_HEIGHT) // 2)
    ball = Ball()
    # Main game loop
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            left_paddle.move("up")
        if keys[pygame.K_s]:
            left_paddle.move("down")
        if keys[pygame.K_UP]:
            right_paddle.move("up")
        if keys[pygame.K_DOWN]:
            right_paddle.move("down")

        ball.update([left_paddle, right_paddle])

        screen.fill(BLACK)
        left_paddle.draw(screen)
        right_paddle.draw(screen)
        ball.draw(screen)
        pygame.draw.aaline(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
