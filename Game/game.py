from game_properties import *
from Paddle import Paddle
from gameService import *
import sys
from peer import Peer
from dataclasses import dataclass, asdict
import json 

@dataclass
class GameState:
    paddle: Paddle
    ball: Ball = None  # Ball can be None for non-owners
    score: list = None

    def to_json(self):
        data = {
            'paddle': self.paddle.to_dict(),
        }
        if self.ball is not None:
            data['ball'] = self.ball.to_dict()
            data['score'] = self.score
        return json.dumps(data, indent=4)
        
class Pong:
    def __init__(self, name, local_client, clients):
        self.paddles = {}
        self.score = [0, 0]
        self.name = name
        self.ball_owner_name = "player1"  # Define the ball owner
        self.is_ball_owner = (name == self.ball_owner_name)
        self.setup_p2p(name, local_client, clients, self.apply_game_state)

        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pong")
        self.clock = pygame.time.Clock()
        self.running = True

        self.paddle = Paddle(WIDTH - PADDLE_WIDTH // 2, HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.paddles[name] = self.paddle  # Add your own paddle to the paddles dictionary
        self.ball = Ball(WIDTH // 2, HEIGHT // 2, add_score=self.add_score)

    def apply_game_state(self, game_state_json, peer_name):
        game_state = json.loads(game_state_json)
        paddle_data = game_state['paddle']
        ball_data = game_state.get('ball', None)
        score = game_state.get('score', None)
        if score is not None:
            self.score = score

        # Update or create the peer's paddle
        if peer_name not in self.paddles:
            paddle = Paddle(
                x=paddle_data['x'],
                y=paddle_data['y'],
                width=paddle_data['width'],
                height=paddle_data['height'],
                speed=paddle_data['speed'],
                color=tuple(paddle_data['color'])
            )
            self.paddles[peer_name] = paddle
        else:
            paddle = self.paddles[peer_name]
            paddle.x = paddle_data['x']
            paddle.y = paddle_data['y']
            paddle.width = paddle_data['width']
            paddle.height = paddle_data['height']
            paddle.speed = paddle_data['speed']
            paddle.color = tuple(paddle_data['color'])

        # Update the ball only if the data is from the ball owner
        if ball_data is not None and peer_name == self.ball_owner_name and not self.is_ball_owner:
            self.ball.x = ball_data['x']
            self.ball.y = ball_data['y']
            self.ball.width = ball_data['width']
            self.ball.height = ball_data['height']
            self.ball.speed_x = ball_data['speed_x']
            self.ball.speed_y = ball_data['speed_y']
            self.ball.color = tuple(ball_data['color'])

    def setup_p2p(self, name, local_client, clients, apply_game_state):
        port = int(local_client.split(":")[1])
        self.peer = Peer(name, port, apply_game_state)

        for client in clients:
            ip, port = client.split(":")
            self.peer.add_peer(ip, int(port))

    def handle_events(self):
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
            if self.is_ball_owner:
                self.peer.send_game_state(GameState(self.paddle, self.ball, self.score))
            else:
                self.peer.send_game_state(GameState(self.paddle))
            self.clock.tick(60)

    def _update(self):
        keys = pygame.key.get_pressed()
        handle_paddle_movement(keys, self.paddle)

        if self.is_ball_owner:
            # Update the ball only if you are the owner
            self.ball.update(list(self.paddles.values()))

    def _draw(self):
        self.screen.fill(BLACK)
        for paddle in self.paddles.values():
            paddle.draw(self.screen)
        self.ball.draw(self.screen)
        pygame.draw.aaline(self.screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

        # Draw score
        font = pygame.font.Font(None, 74)
        score_text = font.render(f"{self.score[0]} : {self.score[1]}", True, WHITE)
        score_text_rect = score_text.get_rect(center=(WIDTH // 2, 50))
        self.screen.blit(score_text, score_text_rect)

        pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()
