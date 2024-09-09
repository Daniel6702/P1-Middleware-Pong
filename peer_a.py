import zmq
import time

context = zmq.Context()

socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

print("Peer A: Sending message to Peer B...")

socket.send_string("Hello from Peer A!")
message = socket.recv_string() 
print(f"Peer A received: {message}")

time.sleep(1)
socket.send_string("How are you, Peer B?")
message = socket.recv_string()
print(f"Peer A received: {message}")
