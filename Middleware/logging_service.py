from Middleware.peer import Peer
import threading
import queue
import time

class LoggingService:
    def __init__(self, peer: 'Peer'):
        self.peer = peer
        self.init_transmission_time()
        self.init_dropout_rate()
        self.init_real_time_constraints()

    def init_real_time_constraints(self):
        self.max_allowed_latency = 0.1 # 100 ms
        self.real_time_violations = 0
        self.real_time_lock = threading.Lock()
        real_time_logging_thread = threading.Thread(target=self.log_real_time_constraints, daemon=True)
        real_time_logging_thread.start()

    def init_dropout_rate(self):
        self.sent_messages = set()
        self.received_messages = set()
        self.dropout_lock = threading.Lock()
        dropout_logging_thread = threading.Thread(target=self.log_dropout_rate, daemon=True)
        dropout_logging_thread.start()

    def init_transmission_time(self):
        self.transmission_times = queue.Queue()
        self.transmission_lock = threading.Lock()
        logging_thread = threading.Thread(target=self.log_transmission_times, daemon=True)
        logging_thread.start()

    def log_transmission_times(self):
        with open("transmission_times.log", "a") as f:
            while True:
                try:
                    transmission_time = self.transmission_times.get(timeout=10)
                    f.write(f"{transmission_time}\n")
                except queue.Empty:
                    continue

    def log_dropout_rate(self):
        with open("dropout_rate.log", "a") as f:
            while True:
                time.sleep(60)  # Log every minute
                with self.dropout_lock:
                    sent = len(self.sent_messages)
                    received = len(self.received_messages)
                    dropped = sent - received
                    dropout_rate = (dropped / sent) * 100 if sent > 0 else 0
                    f.write(f"{time.time()},{sent},{received},{dropped},{dropout_rate}\n")
                    print(f"Dropout Rate: {dropout_rate:.2f}%")

    def log_real_time_constraints(self):
        with open("real_time_constraints.log", "a") as f:
            while True:
                time.sleep(60)  # Log every minute
                with self.real_time_lock:
                    violations = self.real_time_violations
                    f.write(f"{time.time()},{violations}\n")
                    print(f"Real-Time Violations: {violations}")
                    # Reset counter after logging
                    self.real_time_violations = 0

    def increment_real_time_violations(self):
        with self.real_time_lock:
            self.real_time_violations += 1