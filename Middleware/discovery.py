import threading
import time
import json
import socket
from Middleware.utils import get_broadcast_address
from properties import UDP_BROADCAST_PORT, PRESENCE_BROADCAST_INTERVAL
from properties import KEY
from Middleware.peer import Peer
from Middleware.message import Message 

UDP_BROADCAST_IP = get_broadcast_address()

'''
UDP Discovery Service
    - Create message with id, ip, port
    - Encrypt message with XOR encryption
    - Broadcast encrypted message over UDP
    - Listen for UDP messages
    - Decrypt message with XOR encryption
    - Parse message and call on_peer_found callback
'''

class DiscoveryService:
    def __init__(self, peer: 'Peer'):
        """
        Initialize the DiscoveryService with XOR encryption.

        :param peer: Instance of the Peer class.
        """
        if not isinstance(KEY, bytes) or len(KEY) != 4:
            raise ValueError("Key must be a 4-byte (32-bit) bytes object.")
        
        self.peer = peer
        self.setup_udp_discovery()
        self.start_discovery()

    def _xor_cipher(self, data: bytes) -> bytes:
        """
        Encrypt or decrypt data using XOR with the pre-shared key.

        :param data: Data to encrypt/decrypt.
        :return: Encrypted/decrypted data.
        """
        return bytes([b ^ KEY[i % len(KEY)] for i, b in enumerate(data)])

    def setup_udp_discovery(self):
        # Setup UDP socket for broadcasting
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_socket.settimeout(0.2)  # Non-blocking with timeout

        # Setup UDP socket for listening
        self.udp_listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_listener.bind(('', UDP_BROADCAST_PORT))
        self.udp_listener.settimeout(0.2)  # Non-blocking with timeout

    def listen_udp(self):
        while not self.discovery_stop_event.is_set():
            try:
                encrypted_data, addr = self.udp_listener.recvfrom(4096)  # Increased buffer size if needed
                decrypted_data = self._xor_cipher(encrypted_data)
                message_str = decrypted_data.decode('utf-8')
                message = Message.from_json(message_str)
                
                if message is None:
                    continue  # Skip processing if message couldn't be decoded

                msg_type = message.type
                if msg_type == "presence":
                    sender_id = message.id
                    sender_ip = message.data.get("ip")
                    sender_port = message.data.get("port")
                    sender_ready = message.data.get("ready")
                    if sender_id and sender_ip and sender_port:
                        if sender_id != str(self.peer.id):
                            self.peer.add_peer(sender_ip, sender_port, sender_id)
                            print(f"DiscoveryService: Found peer {sender_id} at {sender_ip}:{sender_port}")
            except socket.timeout:
                continue
            except UnicodeDecodeError:
                print("Failed to decode decrypted UDP message. Possible wrong key.")
            except json.JSONDecodeError:
                print("Received invalid JSON message over UDP.")
            except Exception as e:
                print(f"Error in UDP listener: {e}")

    def broadcast_presence(self, interval=1):
        while not self.discovery_stop_event.is_set():
            # Create a Message instance for presence
            presence_message = Message(
                id=str(self.peer.id),
                type="presence",
                data={
                    "ip": self.peer.ip,
                    "port": self.peer.bind_port,
                    "ready": self.peer.ready
                }
            )
            serialized_message = presence_message.to_json()
            message_bytes = serialized_message.encode('utf-8')
            encrypted_message = self._xor_cipher(message_bytes)
            # Broadcast over UDP
            try:
                self.udp_socket.sendto(encrypted_message, (UDP_BROADCAST_IP, UDP_BROADCAST_PORT))
                print(f"DiscoveryService: Node {self.peer.id} broadcasted encrypted presence via UDP.")
            except Exception as e:
                print(f"Error broadcasting presence: {e}")
            time.sleep(interval)

    def stop_discovery(self):
        # Stop UDP listener thread
        self.discovery_stop_event.set()
        if hasattr(self, 'udp_listener_thread') and self.udp_listener_thread.is_alive():
            self.udp_listener_thread.join()
            print(f"DiscoveryService: Node {self.peer.id} UDP listener thread stopped.")

        # Stop UDP broadcast thread
        if hasattr(self, 'discovery_thread') and self.discovery_thread.is_alive():
            self.discovery_thread.join()
            print(f"DiscoveryService: Node {self.peer.id} UDP broadcast thread stopped.")

    def start_discovery(self):
        # Initialize the stop event
        self.discovery_stop_event = threading.Event()

        # Start UDP listener thread
        self.udp_listener_thread = threading.Thread(target=self.listen_udp, daemon=True)
        self.udp_listener_thread.start()
        print(f"DiscoveryService: Node {self.peer.id} UDP listener thread started.")

        # Start UDP broadcast thread
        self.discovery_thread = threading.Thread(target=self.broadcast_presence, args=(PRESENCE_BROADCAST_INTERVAL,), daemon=True)
        self.discovery_thread.start()
        print(f"DiscoveryService: Node {self.peer.id} UDP broadcast thread started.")

    def kill(self):
        self.stop_discovery()
        self.udp_socket.close()
        self.udp_listener.close()
        print(f"DiscoveryService: Node {self.peer.id} discovery service stopped.")
