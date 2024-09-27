import pygame
from game_properties import *
from .Paddle import Paddle
from .Ball import Ball
from .gameService import *
import sys
from peer import Peer
from dataclasses import dataclass, asdict
import json 

@dataclass
class GameState:
    paddle: Paddle
    ball: Ball
    
    def to_json(self):
        return json.dumps(asdict(self), indent=4)

class Pong:
    def __init__(self, name, local_client, clients):
        self.setup_p2p(name, local_client, clients, self.apply_game_state)
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pong")
        self.clock = pygame.time.Clock()
        self.running = True

        self.balls = []
        self.paddles = []

        self.paddle = Paddle(10, HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.ball = Ball(WIDTH // 2, HEIGHT // 2)

    def apply_game_state(self, game_state, peer_name):
        game_state = json.loads(game_state)
        paddle = Paddle(**game_state["paddle"])
        ball = Ball(**game_state["ball"])
        self.balls.append(ball)
        self.paddles.append(paddle)

    def setup_p2p(self, name, local_client, clients, apply_game_state):
        port = int(local_client.split(":")[1])
        self.peer = Peer(name,port, apply_game_state)

        for client in clients:
            ip, port = client.split(":")
            self.peer.add_peer(ip, int(port))

    def handle_events(self):
        """Handle user input and events like quitting the game."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def run(self):
        while self.running:
            self.handle_events()
            self._update()
            self._draw()
            self.peer.send_game_state(GameState(self.paddle, self.ball).to_json())
            self.clock.tick(60)

    def _update(self):
        keys = pygame.key.get_pressed()
        handle_paddle_movement(keys, self.paddle)

        for ball in self.balls+[self.ball]:
            update_game_objects(ball, self.paddles+[self.paddle])

    def _draw(self):
        self.screen.fill(BLACK)
        self.paddle.draw(self.screen)
        self.ball.draw(self.screen)
        for paddle in self.paddles:
            paddle.draw(self.screen)
        for ball in self.balls:
            ball.draw(self.screen)
        pygame.draw.aaline(self.screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
        pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()