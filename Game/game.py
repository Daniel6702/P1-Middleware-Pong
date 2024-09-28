import pygame
from properties import *
from .Paddle import Paddle
from .Ball import Ball
from .gameService import *
import sys
from Middleware.peer import Peer
from dataclasses import dataclass, asdict
import json 

@dataclass
class GameState:
    paddle: 'Paddle'
    ball: 'Ball' = None  # Ball can be None for non-owners
    score: list = None

    def to_json(self):
        data = {
            'paddle': self.paddle.to_dict(),
        }
        if self.ball is not None:
            data['ball'] = self.ball.to_dict()
            data['score'] = self.score
        return json.dumps(data)

class Pong:
    def __init__(self, peer: Peer, name: str = "player1"):
        self.peer = peer
        self.peer.on_message_received = self.on_message_received

        self.paddles = {}
        self.score = [0, 0]
        self.name = name

        # Determine leadership status
        self.is_leader = self.peer.is_leader

        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Multiplayer Pong")
        self.clock = pygame.time.Clock()
        self.running = True

        # Initialize your paddle
        self.paddle = Paddle(
            x=WIDTH - PADDLE_WIDTH - 10 if self.is_leader else 10,  # Position based on role
            y=HEIGHT // 2 - PADDLE_HEIGHT // 2
        )
        self.paddles[self.name] = self.paddle  # Add your own paddle to the paddles dictionary

        # Initialize the ball only if this peer is the leader
        if self.is_leader:
            self.ball = Ball(
                x=WIDTH // 2 - BALL_SIZE // 2,
                y=HEIGHT // 2 - BALL_SIZE // 2,
                add_score=self.add_score
            )
        else:
            self.ball = None  # Non-leaders don't own the ball

    def on_message_received(self, message):
        """
        Callback for handling incoming messages from peers.
        Expects 'data' type messages containing game state JSON.
        """
        msg_type = message.get("type")
        if msg_type == "game_state":
            game_state_json = message.get("data", "")
            sender_id = message.get("id", "")
            self.apply_game_state(game_state_json, sender_id)

    def apply_game_state(self, game_state_json: str, sender_id: str):
        """
        Apply the received game state to update local game objects.
        """
        try:
            game_state = json.loads(game_state_json)
            paddle_data = game_state['paddle']
            ball_data = game_state.get('ball', None)
            score = game_state.get('score', None)

            if score is not None:
                self.score = score

            # Update or create the sender's paddle
            peer_name = self.get_peer_name_by_id(sender_id)
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
                paddle.update_from_dict(paddle_data)

            # Update the ball only if the sender is the leader and this peer is not the leader
            if ball_data and self.peer.leader_id == sender_id and not self.is_leader:
                if self.ball is None:
                    self.ball = Ball(add_score=self.add_score)  # Initialize if not present
                self.ball.update_from_dict(ball_data)
        except json.JSONDecodeError:
            print("Received invalid game state JSON.")
        except Exception as e:
            print(f"Error applying game state: {e}")

    def get_peer_name_by_id(self, peer_id: str) -> str:
        """
        Map a peer ID to a human-readable peer name.
        Customize this method based on how you manage peer identities.
        """
        # Placeholder implementation: Assign names based on peer order
        for index, (address, pid) in enumerate(self.peer.get_peers(), start=2):
            if pid == peer_id:
                return f"player{index}"
        return "unknown"

    def handle_events(self):
        """
        Handle user input events.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.paddle.move("up")
        if keys[pygame.K_DOWN]:
            self.paddle.move("down")

    def add_score(self, player: int):
        """
        Update the score for the specified player.
        """
        if 0 <= player < len(self.score):
            self.score[player] += 1

    def run(self):
        """
        Main game loop.
        """
        while self.running:
            self.handle_events()
            self._update()
            self._draw()

            # Prepare and send game state
            if self.is_leader:
                game_state = GameState(self.paddle, self.ball, self.score)
            else:
                game_state = GameState(self.paddle)
            self.peer.send_public_message(
                message=json.loads(game_state.to_json()),
                type="game_state"
            )

            self.clock.tick(60)  # Maintain 60 FPS

        self.quit()

    def _update(self):
        """
        Update game objects.
        """
        if self.is_leader and self.ball:
            self.ball.update(list(self.paddles.values()))

    def _draw(self):
        """
        Render the game state to the screen.
        """
        self.screen.fill(BLACK)
        for paddle in self.paddles.values():
            paddle.draw(self.screen)
        if self.ball:
            self.ball.draw(self.screen)
        pygame.draw.aaline(self.screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

        # Render the score
        font = pygame.font.Font(None, 74)
        score_text = font.render(f"{self.score[0]} : {self.score[1]}", True, WHITE)
        score_text_rect = score_text.get_rect(center=(WIDTH // 2, 50))
        self.screen.blit(score_text, score_text_rect)

        pygame.display.flip()

    def quit(self):
        """
        Cleanly exit the game.
        """
        pygame.quit()
        sys.exit()