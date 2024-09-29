import threading
import time
import queue
from Middleware.peer import Peer
import threading
import time
import queue
from properties import ELECTION_TIMEOUT, ELECTION_TIMEOUT_CHECK, HEARTBEAT_INTERVAL
from Middleware.utils import uuid_to_number

'''
Bully Algorithm Leader Selection Service
    - Initiates leader election using the Bully Algorithm
    - Handles leader election messages (ELECTION, ANSWER, COORDINATOR)
    - Monitors leader heartbeats and initiates new elections if needed
    - Sends heartbeats if the node is the leader
'''

class LeaderSelectionService:
    def __init__(self, peer: Peer):
        """
        Initialize the LeaderSelectionService.

        :param peer: Instance of the Peer class.
        """
        self.peer = peer
        self.election_in_progress = False
        self.heartbeat_last_received = time.time()
        self.lock = threading.RLock()  # Changed from threading.Lock to threading.RLock

        # Initialize the message queue
        self.receive_leader_message_queue = queue.Queue()

        # Start heartbeat monitoring thread
        self.heartbeat_thread = threading.Thread(target=self.monitor_heartbeat, daemon=True)
        self.heartbeat_thread.start()

        # Start handling leader election messages
        self.leader_thread = threading.Thread(target=self.handle_leader_messages, daemon=True)
        self.leader_thread.start()

    def monitor_heartbeat(self):
        """
        Monitor the heartbeat from the leader. If heartbeats are not received within the timeout,
        initiate a new election.
        """
        while True:
            time.sleep(ELECTION_TIMEOUT_CHECK)
            with self.lock:
                if self.peer.is_leader:
                    continue  # Leader doesn't need to monitor heartbeats
                elapsed = time.time() - self.heartbeat_last_received
                if elapsed > ELECTION_TIMEOUT:
                    print(f"Node: {self.peer.id} detected leader timeout. Initiating election.")
                    self.initiate_election()

    def initiate_election(self):
        """
        Initiate the Bully Algorithm election process by sending ELECTION messages
        to all peers with higher IDs.
        """
        with self.lock:
            if self.election_in_progress:
                print(f"Node: {self.peer.id} election already in progress. Aborting new initiation.")
                return  # Avoid multiple simultaneous elections
            self.election_in_progress = True

        higher_peers = [peer for peer in self.peer.peers if uuid_to_number(peer[1]) > uuid_to_number(self.peer.id)]
        if not higher_peers:
            # No higher peers, declare self as leader
            self.declare_leader()
            with self.lock:
                self.election_in_progress = False
            return

        # Send ELECTION message to all higher peers
        election_message = {
            "type": "election",
            "id": str(self.peer.id)
        }
        for peer_info in higher_peers:
            self.peer.send_private_message(peer_info[0], election_message, type="election")

        # Wait for ANSWER messages
        def wait_for_responses():
            time.sleep(ELECTION_TIMEOUT_CHECK)
            with self.lock:
                if self.peer.leader_id is None:
                    self.declare_leader()
                self.election_in_progress = False

        wait_thread = threading.Thread(target=wait_for_responses, daemon=True)
        wait_thread.start()

    def declare_leader(self):
        """
        Declare self as the leader and notify all peers by sending COORDINATOR messages.
        Also starts sending heartbeats.
        """
        self.peer.is_leader = True
        self.peer.leader_id = self.peer.id
        print(f"Node: {self.peer.id} is declaring itself as the leader.")
        coordinator_message = {
            "type": "coordinator",
            "id": str(self.peer.id)
        }
        # Broadcast COORDINATOR message to all peers
        for peer_info in self.peer.peers:
            self.peer.send_private_message(peer_info[0], coordinator_message, type="coordinator")
        # Start sending heartbeats
        heartbeat_thread = threading.Thread(target=self.send_heartbeats, daemon=True)
        heartbeat_thread.start()

    def send_heartbeats(self):
        """
        If the node is the leader, periodically send heartbeat messages to all peers.
        """
        while self.peer.is_leader:
            print(f"Node: {self.peer.id} sending heartbeat.")
            self.peer.send_public_message({}, type="heartbeat")
            time.sleep(HEARTBEAT_INTERVAL)

    def handle_leader_messages(self):
        """
        Continuously process incoming leader election messages from the queue.
        """
        while True:
            try:
                message = self.receive_leader_message_queue.get(timeout=1)
                msg_type = message.get("type")
                msg_id = message.get("id")
                if msg_type == "election":
                    self.handle_election_message(msg_id)
                elif msg_type == "answer":
                    self.handle_answer_message(msg_id)
                elif msg_type == "coordinator":
                    self.handle_coordinator_message(msg_id)
                elif msg_type == "heartbeat":
                    self.handle_heartbeat_message(msg_id)
            except queue.Empty:
                continue

    def handle_election_message(self, sender_id):
        """
        Handle incoming ELECTION messages by sending an ANSWER and initiating own election.

        :param sender_id: UUID of the peer that sent the ELECTION message.
        """
        print(f"Node: {self.peer.id} received ELECTION message from {sender_id}.")
        # Send ANSWER message back
        answer_message = {
            "type": "answer",
            "id": str(self.peer.id)
        }
        sender_peer = self.peer.get_peer_by_id(sender_id)
        if sender_peer:
            self.peer.send_private_message(sender_peer[0], answer_message, type="answer")
        # Initiate own election if not already in progress
        self.initiate_election()

    def handle_answer_message(self, sender_id):
        """
        Handle incoming ANSWER messages by acknowledging that a higher peer is alive.

        :param sender_id: UUID of the peer that sent the ANSWER message.
        """
        print(f"Node: {self.peer.id} received ANSWER message from {sender_id}.")
        # A higher peer is alive, wait for coordinator message
        with self.lock:
            self.peer.leader_id = sender_id  # Tentatively accept the higher peer as leader

    def handle_coordinator_message(self, sender_id):
        """
        Handle incoming COORDINATOR messages by updating the leader information.

        :param sender_id: UUID of the peer that sent the COORDINATOR message.
        """
        print(f"Node: {self.peer.id} received COORDINATOR message from {sender_id}.")
        with self.lock:
            self.peer.leader_id = sender_id
            self.peer.is_leader = (self.peer.id == sender_id)
            if self.peer.is_leader:
                print(f"Node: {self.peer.id} is confirmed as the leader.")
                # Start sending heartbeats if not already
                heartbeat_thread = threading.Thread(target=self.send_heartbeats, daemon=True)
                heartbeat_thread.start()
            else:
                print(f"Node: {self.peer.id} recognizes {sender_id} as the leader.")
        self.heartbeat_last_received = time.time()

    def handle_heartbeat_message(self, sender_id):
        """
        Handle incoming HEARTBEAT messages by updating the last received heartbeat time.

        :param sender_id: UUID of the leader that sent the HEARTBEAT message.
        """
        # Update the last heartbeat time
        with self.lock:
            if self.peer.leader_id != sender_id:
                self.peer.leader_id = sender_id
                print(f"Node: {self.peer.id} updated leader to {sender_id} based on heartbeat.")
            self.heartbeat_last_received = time.time()

    def shutdown(self):
        """
        Cleanly shut down the LeaderSelectionService.
        """
        # No explicit shutdown logic required as threads are daemons
        print(f"LeaderSelectionService for Node: {self.peer.id} is shutting down.")

