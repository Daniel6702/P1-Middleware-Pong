from pygame import constants, draw, display
from game_properties import WIDTH, HEIGHT, BLACK, WHITE
from Game.Ball import Ball

def handle_paddle_movement(keys, paddle):
    """Handle paddle movement based on key input."""
    if keys[constants.K_w]:
        paddle.move("up")
    if keys[constants.K_s]:
        paddle.move("down")

def update_game_objects(ball: Ball, paddles):
    """Update the ball and check for collisions with paddles."""
    ball.update(paddles)

def render_game(screen, left_paddle, right_paddle, ball):
    """Render all the game objects onto the screen."""
    screen.fill(BLACK)
    left_paddle.draw(screen)
    right_paddle.draw(screen)
    ball.draw(screen)
    draw.aaline(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
    display.flip()
