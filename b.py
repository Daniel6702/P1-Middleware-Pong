from peer import Peer

peer = Peer("Bob", 5556)
peer.add_peer("localhost", 5555)
peer.keep_alive() 
