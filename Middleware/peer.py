import zmq
import threading
import json
import random
import uuid
from properties import POLL_RATE
from Middleware.utils import get_ipv4
from Middleware.message import Message
from dataclasses import asdict

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
        self.ready = False # Ready state

        self.setup_zmq()

        # Initialize DiscoveryService
        from Middleware.discovery import DiscoveryService
        self.discovery_service = DiscoveryService(self)

        # Initialize LeaderSelectionService
        from Middleware.leader_selection import LeaderSelectionService
        self.leader_service = LeaderSelectionService(self)

    def get_peers(self):
        return self.peers

    def setup_zmq(self):
        # ZeroMQ context
        self.context = zmq.Context()

        # Create publisher socket to send messages to other peers
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind(f"tcp://*:{self.bind_port}") 

        # ZeroMQ SUB socket to receive messages from other peers
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
        self.subscriber.setsockopt(zmq.RCVTIMEO, 10000)
        
        # Start the receiver thread
        receiver_thread = threading.Thread(target=self.receive_message, daemon=True)
        receiver_thread.start()        

    def add_peer(self, ip: str, port: int, peer_id: str, peer_ready: bool):
        if ip == self.ip and port == self.bind_port: 
            return

        peer_address = f"{ip}:{port}"
        if peer_address not in self.peers:
            self.subscriber.connect(f"tcp://{ip}:{port}")
            self.peers.add((peer_address, peer_id, peer_ready))
            print(f"Node: {self.id} connected to peer at {ip}:{port} with peer_id {peer_id}")
        else:
            print(f"Node: {self.id} already connected to peer at {ip}:{port} with peer_id {peer_id}")

    # Use the publisher socket to send messages to other peers
    def send_public_message(self, message: Message):
        serialized_message = message.to_json()
        self.publisher.send_string(serialized_message)
        print(f"Node: {self.id} sent {message.type} message: {serialized_message}")

    # Use the subscriber socket to receive messages from other peers
    def receive_message(self):
        poller = zmq.Poller()
        poller.register(self.subscriber, zmq.POLLIN)
        
        while True:
            try:
                socks = dict(poller.poll(POLL_RATE)) 

                if self.subscriber in socks and socks[self.subscriber] == zmq.POLLIN:
                    raw_message = self.subscriber.recv_string()
                    message = Message.from_json(raw_message)
                    if message is None:
                        continue  # Skip processing if message couldn't be decoded

                    # Handle the message based on its type
                    if message.type in ["election", "answer", "coordinator", "heartbeat"]:
                        self.leader_service.receive_leader_message_queue.put(message)
                    else:
                        self.on_message_received(message)
                        print(f"Node: {self.id} received message: {message}")

            except Exception as e: 
                print(f"Error receiving message: {e}")

    def send_private_message(self, address: str, message: Message):
        serialized_message = message.to_json()
        try:
            temp_socket = self.context.socket(zmq.PUSH)
            temp_socket.connect(f"tcp://{address}")
            temp_socket.send_string(serialized_message)
            temp_socket.close()
            print(f"Node: {self.id} sent {message.type} message to {address}")
        except Exception as e:
            print(f"Error sending message to peer {address}: {e}")

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
        print(f"{self.id} shut down successfully.")
