import pygame
from properties import *
from .Paddle import Paddle
from .Ball import Ball
from .gameService import *
import sys
from Middleware.peer import Peer
import json 
from Middleware.message import Message
from Game.GameState import GameState
import time
import threading

class Pong:
    def __init__(self, peer: 'Peer', name: str = "player1"):
        #Initialize Pygame
        self.init_pygame()

        # Initialize Game variables
        self.score = [0, 0]
        self.paddle = Paddle(x = WIDTH // 2, y = HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.paddles = {name : self.paddle}
        self.ball = None  
        self.is_running = False
        self.countdown = None

        # Initialize Middleware
        self.peer = peer
        self.peers_ingame = set()
        self.is_peers_organized = False
        self.is_leader = self.peer.is_leader
        self.peer.on_message_received = self.on_message_received

        # --- TEST ---
        #self.start_game()
        # --- TEST ---

    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Multiplayer Pong")
        self.clock = pygame.time.Clock()
        self.running = True

    def start_game(self):
        def logic():
            print("Starting game")
            #Begin countdown
            for i in range(3,0,-1):
                print(i)
                countdown_message = Message(
                    id = str(self.peer.id),
                    type = "countdown",
                    data = {"value": i}
                )
                self.countdown = i
                self.peer.send_public_message(countdown_message)
                time.sleep(1.5)
            #Create Ball
            self.ball = Ball(
                    x=WIDTH // 2 - BALL_SIZE // 2,
                    y=HEIGHT // 2 - BALL_SIZE // 2,
                    add_score=self.add_score
                )
            #Organize players into teams
            self.organize_peers()
            #Send "Begin" message
            countdown_message = Message(
                id = str(self.peer.id),
                type = "countdown",
                data = {"value": "begin"}
            ) 
            self.countdown = None
            self.peer.send_public_message(countdown_message)
            self.is_running = True
        start_thread = threading.Thread(target=logic)
        start_thread.start()

    def organize_peers(self):
        print("Organizing peers")
        """
        Organize the peers in the game.
        """
        self.paddle.x = WIDTH - PADDLE_WIDTH - 10
        for i, peer in enumerate(self.peer.peers):
            if i % 2 == 0:
                side_message = Message(
                    id=str(self.peer.id),
                    type="side",
                    data={"side": "left"}
                )
            else:
                side_message = Message(
                    id=str(self.peer.id),
                    type="side",
                    data={"side": "right"}
                )
            self.peer.send_private_message(peer[1], side_message)
        self.is_peers_organized = True

    def on_message_received(self, message: Message):
        """
        Callback for handling incoming messages from peers.
        Expects 'game_state' type messages containing game state data.
        """
        msg_type = message.type
        if msg_type == "game_state":
            game_state_data = message.data.get("game_state")
            sender_id = message.id
            self.apply_game_state(game_state_data, sender_id)

        elif msg_type == "ingame":
            self.peers_ingame.add(message.id)
            if self.is_leader and len(self.peers_ingame) >= len(self.peer.peers) and not self.is_peers_organized:
                self.start_game()

        elif msg_type == "side":
            side = message.data.get("side")
            if side:
                if side == "left":
                    self.paddle.x = 10
                elif side == "right":
                    self.paddle.x = WIDTH - PADDLE_WIDTH - 10

        elif msg_type == "countdown":
            value = message.data.get("value")
            if value == "begin":
                self.is_running = True
                self.countdown = None
            else:
                self.countdown = value

    def text(self, txt: str, x: int, y: int, font_size: int = 20, color: tuple = WHITE):
        font = pygame.font.SysFont(None, font_size)
        surface = font.render(txt, True, color)
        self.screen.blit(surface, (x, y))

    def display_countdown(self, value_to_display):
        center_y = HEIGHT // 2
        self.text(
            txt = str(value_to_display),
            x = WIDTH // 4,
            y = center_y,
            font_size = 100,
            color=(0,255,0)
        )
        self.text(
            txt = str(value_to_display),
            x = 3 * (WIDTH // 4),
            y = center_y,
            font_size = 100,
            color=(0,255,0)
        )

    def apply_game_state(self, game_state_data: dict, sender_id: str):
        """
        Apply the received game state to update local game objects.
        """
        try:
            # Create a GameState instance from the received data
            game_state = GameState.from_dict(game_state_data)
            paddle_data = game_state.paddle.to_dict()
            ball_data = game_state.ball.to_dict() if game_state.ball else None
            score = game_state.score

            if score is not None:
                self.score = score

            # Update or create the sender's paddle
            peer_name = self.get_peer_name_by_id(sender_id)
            if peer_name not in self.paddles:
                paddle = Paddle.from_dict(paddle_data)
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
            self.clock.tick(FPS)  

        self.quit()

    def _update(self):
        """
        Update game objects.
        """
        if self.is_leader and self.ball:
            self.ball.update(list(self.paddles.values()))

        if self.is_running:
            if self.is_leader and self.ball:
                game_state = GameState(self.paddle, self.ball, self.score)
            else:
                game_state = GameState(self.paddle)
            
            # Create a Message instance for game_state
            game_state_message = Message(
                id=str(self.peer.id),
                type="game_state",
                data={
                    "game_state": game_state.to_dict()
                }
            )
            self.peer.send_public_message(game_state_message)
        else:
            ingame_message = Message(
                id = str(self.peer.id),
                type = "ingame",
                data = {}
            )
            self.peer.send_public_message(ingame_message)

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

        # Render countdown
        if self.countdown:
            self.display_countdown(self.countdown)

        pygame.display.flip()

    def quit(self):
        """
        Cleanly exit the game.
        """
        pygame.quit()
        sys.exit()

