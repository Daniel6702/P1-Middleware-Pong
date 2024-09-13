from peer import Peer

peer = Peer("Alice", 5555)
peer.add_peer("localhost", 5556)
peer.keep_alive()