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
        return json.dumps({
            'paddle': self.paddle.to_dict(),
            'ball': self.ball.to_dict()
        }, indent=4)
    
class Pong:
    def __init__(self, name, local_client, clients):
        self.balls = []
        self.paddles = []
        self.peers_paddles = {}
        self.peers_balls = {}
        self.score = [0, 0]
        self.setup_p2p(name, local_client, clients, self.apply_game_state)

        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pong")
        self.clock = pygame.time.Clock()
        self.running = True

        self.paddle = Paddle(PADDLE_WIDTH // 2, HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.ball = Ball(WIDTH // 2, HEIGHT // 2, add_score=self.add_score)

        

    def apply_game_state(self, game_state_json, peer_name):
        # Deserialize the JSON string
        game_state = json.loads(game_state_json)
        paddle_data = game_state['paddle']
        ball_data = game_state['ball']

        # Update or create the peer's paddle
        if peer_name not in self.peers_paddles:
            # Create new paddle
            paddle = Paddle(
                x=paddle_data['x'],
                y=paddle_data['y'],
                width=paddle_data['width'],
                height=paddle_data['height'],
                speed=paddle_data['speed'],
                color=tuple(paddle_data['color'])
            )
            self.peers_paddles[peer_name] = paddle
        else:
            # Update existing paddle
            paddle = self.peers_paddles[peer_name]
            paddle.x = paddle_data['x']
            paddle.y = paddle_data['y']
            paddle.width = paddle_data['width']
            paddle.height = paddle_data['height']
            paddle.speed = paddle_data['speed']
            paddle.color = tuple(paddle_data['color'])

        # Update or create the peer's ball
        if peer_name not in self.peers_balls:
            # Create new ball
            ball = Ball(
                x=ball_data['x'],
                y=ball_data['y'],
                width=ball_data['width'],
                height=ball_data['height'],
                speed_x=ball_data['speed_x'],
                speed_y=ball_data['speed_y'],
                color=tuple(ball_data['color'],
                            add_score=self.add_score)
            )
            self.peers_balls[peer_name] = ball
        else:
            # Update existing ball
            ball = self.peers_balls[peer_name]
            ball.x = ball_data['x']
            ball.y = ball_data['y']
            ball.width = ball_data['width']
            ball.height = ball_data['height']
            ball.speed_x = ball_data['speed_x']
            ball.speed_y = ball_data['speed_y']
            ball.color = tuple(ball_data['color'])


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
    
    def add_score(self, player):
        self.score[player] += 1

    def run(self):
        while self.running:
            self.handle_events()
            self._update()
            self._draw()
            self.peer.send_game_state(GameState(self.paddle, self.ball))
            self.clock.tick(60)

    def _update(self):
        keys = pygame.key.get_pressed()
        handle_paddle_movement(keys, self.paddle)

        # Update only your own ball
        update_game_objects(self.ball, [self.paddle] + list(self.peers_paddles.values()))

    def _draw(self):
        self.screen.fill(BLACK)
        self.paddle.draw(self.screen)
        self.ball.draw(self.screen)
        for paddle in self.peers_paddles.values():
            paddle.draw(self.screen)
        for ball in self.peers_balls.values():
            ball.draw(self.screen)
        pygame.draw.aaline(self.screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

        #draw score
        font = pygame.font.Font(None, 74)
        score_text = font.render(f"{self.score[0]} : {self.score[1]}", True, WHITE)
        score_text_rect = score_text.get_rect(center=(WIDTH // 2, 50))
        self.screen.blit(score_text, score_text_rect)

        pygame.display.flip()


    def quit(self):
        pygame.quit()
        sys.exit()