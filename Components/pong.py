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
        # Handle events (quit, input, etc.)
        running = handle_events()

        # Handle paddle movement
        keys = pygame.key.get_pressed()
        handle_paddle_movement(keys, left_paddle, right_paddle)

        # Update ball and check for collisions
        update_game_objects(ball, [left_paddle, right_paddle])

        # Render game objects
        render_game(screen, left_paddle, right_paddle, ball)

        clock.tick(60)

    pygame.quit()
