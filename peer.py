import zmq
import threading
import time
import json
import random

# ZeroMQ context
context = zmq.Context()

class Peer():
    def __init__(self, peer_name: str, bind_port: int):
        self.peer_name = peer_name

        # Create publisher socket to send game states to other peers
        self.publisher = context.socket(zmq.PUB)
        self.publisher.bind(f"tcp://*:{bind_port}")

        # ZeroMQ SUB socket to receive game states from other peers
        self.subscriber = context.socket(zmq.SUB)
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
        self.subscriber.setsockopt(zmq.RCVTIMEO, 10000)

        # Start the sender and receiver threads
        sender_thread = threading.Thread(target=self.send_game_state)
        receiver_thread = threading.Thread(target=self.receive_game_state)

        sender_thread.daemon = True
        receiver_thread.daemon = True

        sender_thread.start()
        receiver_thread.start()

        print(f"{self.peer_name} initialized and ready.")

    def add_peer(self, ip: str, port: int):
        self.subscriber.connect(f"tcp://{ip}:{port}")
        print(f"{self.peer_name} connected to peer at {ip}:{port}")

    # Use the publisher socket to send game states to other peers
    def send_game_state(self):
        while True:
            game_state = {"peer_name": self.peer_name, "game_state": random.randint(0, 100)}
            self.publisher.send_string(json.dumps(game_state))
            print(f"{self.peer_name} sent game state: {game_state['game_state']}")
            time.sleep(1)  

    # Use the subscriber socket to receive game states from other peers
    def receive_game_state(self):
        while True:
            try:
                message = self.subscriber.recv_string(flags=zmq.NOBLOCK)
                peer_name, state = json.loads(message).values()
                print(f"Received from {peer_name}: {state}")
            except zmq.Again:
                # No message received yet
                pass
            time.sleep(0.01)

    # Keep the main thread alive
    def keep_alive(self):
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"{self.peer_name} shutting down.")

