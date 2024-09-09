import zmq

context = zmq.Context()

socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

print("Peer B: Waiting for message from Peer A...")

message = socket.recv_string()
print(f"Peer B received: {message}")

socket.send_string("Hello from Peer B!")

message = socket.recv_string()
print(f"Peer B received: {message}")

socket.send_string("I'm good, thank you Peer A!")
