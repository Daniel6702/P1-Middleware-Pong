import zmq
import threading
import json
import random
import uuid
from properties import POLL_RATE
from Middleware.utils import get_ipv4
from Middleware.message import Message
from dataclasses import asdict
import time
import queue

class Peer:
    def __init__(self, 
                 ip: str = None, 
                 port: int = None, 
                 on_message_received: callable = lambda: print("Message received")):
        
        self.id = uuid.uuid4()
        self.bind_port = port if port else random.randint(5000, 6000)
        self.ip = ip if ip else get_ipv4()
        self.on_message_received = on_message_received
        self.peers = set()  # Set of tuples: (peer_address, peer_id)
        self.is_leader = False
        self.leader_id = None  # UUID of the current leader

        self.setup_zmq()

        from Middleware.logging_service import LoggingService
        self.logging_service = LoggingService()

        # Initialize DiscoveryService
        from Middleware.discovery_service import DiscoveryService
        self.discovery_service = DiscoveryService(self)

        # Initialize LeaderSelectionService
        from Middleware.leader_election_service import LeaderSelectionService
        self.leader_service = LeaderSelectionService(self)

    def get_peers(self):
        return self.peers

    def setup_zmq(self):
        # ZeroMQ context
        self.context = zmq.Context()

        # --- Setup PUB socket for sending messages ---
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind(f"tcp://*:{self.bind_port}") 

        # --- Setup SUB socket for receiving messages ---
        self.subscriber = self.context.socket(zmq.SUB)
        # Subscribe to public messages
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "public")
        # Subscribe to private messages addressed to this peer
        private_topic = f"private:{self.id}"
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, private_topic)
        self.subscriber.setsockopt(zmq.RCVTIMEO, 10000)
        
        # Start the receiver thread
        receiver_thread = threading.Thread(target=self.receive_message, daemon=True)
        receiver_thread.start()     

    def add_peer(self, ip: str, port: int, peer_id: str):
        if ip == self.ip and port == self.bind_port: 
            return

        peer_address = f"{ip}:{port}"
        if peer_address not in self.peers:
            self.subscriber.connect(f"tcp://{ip}:{port}")
            self.peers.add((peer_address, peer_id))
            print(f"Node: {str(self.id)[:10]} connected to peer at {ip}:{port} with peer_id {peer_id}")
        else:
            print(f"Node: {str(self.id)[:10]} already connected to peer at {ip}:{port} with peer_id {peer_id}")

    # Use the publisher socket to send messages to other peers
    def send_public_message(self, message: Message):
        self.logging_service.on_message_sent(message)
        serialized_message = message.to_json()
        topic = "public"
        full_message = f"{topic} {serialized_message}"
        self.publisher.send_string(full_message)

    # Use the publisher socket to send private messages
    def send_private_message(self, peer_id: str, message: Message):
        self.logging_service.on_message_sent(message)
        topic = f"private:{peer_id}"
        serialized_message = message.to_json()
        full_message = f"{topic} {serialized_message}"
        print(f"Node: {str(self.id)[:10]} sending private message to peer_id {peer_id}")
        self.publisher.send_string(full_message)

    # Use the subscriber socket to receive messages from other peers
    def receive_message(self):
        poller = zmq.Poller()
        poller.register(self.subscriber, zmq.POLLIN)
        
        while True:
            try:
                socks = dict(poller.poll(POLL_RATE))  # Adjust POLL_RATE as needed

                if self.subscriber in socks and socks[self.subscriber] == zmq.POLLIN:
                    raw_message = self.subscriber.recv_string()
                    # Split the message into topic and content
                    try:
                        topic, message_json = raw_message.split(' ', 1)
                    except ValueError:
                        print(f"Received malformed message: {raw_message}")
                        self.logging_service.increment_error_count()
                        continue

                    message = Message.from_json(message_json)
                    if message is None:
                        self.logging_service.increment_error_count()
                        continue

                    self.logging_service.on_message_received(message)

                    # Handle the message based on its type
                    if message.type in ["election", "answer", "coordinator", "heartbeat"]:
                        self.leader_service.receive_leader_message_queue.put(message)
                    else:
                        self.on_message_received(message)
                        #print(f"Node: {str(self.id)[:10]} received message: {message}")

            except zmq.Again:
                # Timeout occurred, can perform other tasks or simply continue
                continue
            except Exception as e: 
                print(f"Error receiving message: {e}")
                self.logging_service.increment_error_count()

    def get_peer_by_id(self, peer_id: str):
        for peer in self.peers:
            if peer[1] == peer_id:
                return peer
        return None

    def kill(self):
        self.publisher.close()
        self.subscriber.close()
        self.context.term()
        self.discovery_service.stop_discovery()
        self.logging_service.kill()
        print(f"{self.id} shut down successfully.")
