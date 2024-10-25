from Middleware.peer import Peer
import threading
import queue
import time
from Middleware.message import Message
import psutil
import statistics
import os
from properties import LOGS_DIR, LOG_RATE
import requests
from datetime import datetime, timedelta

class LogTransmissionTimes:
    def __init__(self):
        self.transmission_times = queue.Queue()
        self.transmission_lock = threading.Lock()
        logging_thread = threading.Thread(target=self.log_transmission_times, daemon=True)
        logging_thread.start()

    def log_transmission_times(self):
        with open(f"{LOGS_DIR}/transmission_times.log", "a", buffering=1) as f:
            while True:
                try:
                    transmission_time = self.transmission_times.get(timeout=LOG_RATE)
                    f.write(f"{transmission_time}\n")
                except queue.Empty:
                    continue

class LogDropoutRate:
    def __init__(self):
        self.sent_messages = []
        self.received_messages = []
        self.dropout_lock = threading.Lock()
        dropout_logging_thread = threading.Thread(target=self.log_dropout_rate, daemon=True)
        dropout_logging_thread.start()

    def log_dropout_rate(self):
        with open(f"{LOGS_DIR}/dropout_rate.log", "a", buffering=1) as f:
            while True:
                time.sleep(LOG_RATE//10)
                with self.dropout_lock:
                    sent = len(self.sent_messages)
                    received = len(self.received_messages)
                    f.write(f"{time.time()},{sent},{received}\n")
                    print(f"Sent: {sent}, Received: {received}")
                    self.sent_messages.clear()
                    self.received_messages.clear()

    def increment_sent_message(self, msg_id):
        with self.dropout_lock:
            self.sent_messages.append(msg_id)

    def increment_received_message(self, msg_id):
        with self.dropout_lock:
            self.received_messages.append(msg_id)

class LogRealTimeViolations:
    def __init__(self):
        self.max_allowed_latency = 0.1 
        self.real_time_violations = 0  
        self.real_time_lock = threading.Lock() 

        real_time_logging_thread = threading.Thread(target=self.log_real_time_constraints, daemon=True)
        real_time_logging_thread.start()

    def log_real_time_constraints(self):
        with open(f"{LOGS_DIR}/real-time_violations.log", "a", buffering=1) as f:
            while True:
                time.sleep(LOG_RATE)
                with self.real_time_lock:
                    violations = self.real_time_violations
                    violations_per_minute = violations * (60 / LOG_RATE)
                    log_entry = f"{time.time()},{violations_per_minute:.2f}\n"
                    f.write(log_entry)
                    print(f"Real-Time Violations: {violations_per_minute:.2f} per minute")
                    self.real_time_violations = 0

    def increment_real_time_violations(self):
        with self.real_time_lock:
            self.real_time_violations += 1

class LogThroughput:
    def __init__(self):
        self.throughput_sent = 0
        self.throughput_received = 0
        self.throughput_lock = threading.Lock()
        throughput_logging_thread = threading.Thread(target=self.log_throughput, daemon=True)
        throughput_logging_thread.start()

    def log_throughput(self): 
        with open(f"{LOGS_DIR}/throughput.log", "a", buffering=1) as f:
            while True:
                time.sleep(LOG_RATE)  
                with self.throughput_lock:
                    sent = self.throughput_sent
                    received = self.throughput_received
                    f.write(f"{time.time()},{sent},{received}\n")
                    print(f"Throughput - Sent: {sent//LOG_RATE}/s, Received: {received//LOG_RATE}/s")
                    self.throughput_sent = 0
                    self.throughput_received = 0
    
    def increment_sent_throughput(self):
        with self.throughput_lock:
            self.throughput_sent += 1
    
    def increment_received_throughput(self):
        with self.throughput_lock:
            self.throughput_received += 1

class LogBandwidth:
    def __init__(self):
        self.bytes_sent = 0
        self.bytes_received = 0
        self.bandwidth_lock = threading.Lock()
        bandwidth_logging_thread = threading.Thread(target=self.log_bandwidth, daemon=True)
        bandwidth_logging_thread.start()

    def log_bandwidth(self):
        with open(f"{LOGS_DIR}/bandwidth.log", "a", buffering=1) as f:
            while True:
                time.sleep(LOG_RATE)
                with self.bandwidth_lock:
                    sent = self.bytes_sent
                    received = self.bytes_received

                    # Calculate MB per minute
                    sent_bandwidth = (sent * (60 / LOG_RATE)) / (1024 * 1024)
                    received_bandwidth = (received * (60 / LOG_RATE)) / (1024 * 1024)

                    f.write(f"{time.time()},{sent_bandwidth:.2f},{received_bandwidth:.2f}\n")
                    print(f"Bandwidth - Sent: {sent_bandwidth:.2f} MB/min, Received: {received_bandwidth:.2f} MB/min")

                    # Reset counters
                    self.bytes_sent = 0
                    self.bytes_received = 0

    def add_bytes_sent(self, byte_count):
        with self.bandwidth_lock:
            self.bytes_sent += byte_count

    def add_bytes_received(self, byte_count):
        with self.bandwidth_lock:
            self.bytes_received += byte_count
class LogErrorRate:
    def __init__(self):
        self.error_count = 0
        self.error_lock = threading.Lock()
        error_logging_thread = threading.Thread(target=self.log_errors, daemon=True)
        error_logging_thread.start()

    def log_errors(self):
        with open(f"{LOGS_DIR}/errors.log", "a", buffering=1) as f:
            while True:
                time.sleep(LOG_RATE)  
                with self.error_lock:
                    errors = self.error_count
                    f.write(f"{time.time()},{errors}\n")
                    print(f"Errors in the last minute: {errors}")
                    self.error_count = 0
    
    def increment_error_count(self):
        with self.error_lock:
            self.error_count += 1

class LogResourceUtilization:
    def __init__(self):
        resource_logging_thread = threading.Thread(target=self.log_resources, daemon=True)
        resource_logging_thread.start()

    def log_resources(self):
        with open(f"{LOGS_DIR}/resources.log", "a", buffering=1) as f:
            while True:
                time.sleep(LOG_RATE)  
                process = psutil.Process()
                cpu_percent = process.cpu_percent(interval=1)  # CPU usage over the last second
                memory_info = process.memory_info()
                memory_usage_mb = memory_info.rss / (1024 * 1024)  # Resident Set Size in MB
                f.write(f"{time.time()},{cpu_percent},{memory_usage_mb}\n")
                print(f"Resource Usage - CPU: {cpu_percent}%, Memory: {memory_usage_mb:.2f} MB")

class LogFPS:
    def __init__(self):
        self.fps_samples = []
        self.fps_lock = threading.Lock()
        fps_logging_thread = threading.Thread(target=self.log_fps, daemon=True)
        fps_logging_thread.start()

    def log_fps(self):
        with open(f"{LOGS_DIR}/fps.log", "a", buffering=1) as f:
            while True:
                time.sleep(LOG_RATE)  
                with self.fps_lock:
                    if self.fps_samples:
                        avg_fps = statistics.mean(self.fps_samples)
                        min_fps = min(self.fps_samples)
                        max_fps = max(self.fps_samples)
                        f.write(f"{time.time()},{avg_fps},{min_fps},{max_fps}\n")
                        print(f"FPS - Avg: {avg_fps:.2f}, Min: {min_fps:.2f}, Max: {max_fps:.2f}")
                        self.fps_samples.clear()
    
    def add_fps_sample(self, fps: float):
        with self.fps_lock:
            self.fps_samples.append(fps)

class LoggingService(
    LogTransmissionTimes,   # Time taken for a message to be sent and received
    LogDropoutRate,         # Rate of messages sent but not received
    LogRealTimeViolations,  # Messages that violate real-time constraints (under stress)
    LogThroughput,          # Number of messages sent and received per second
    LogBandwidth,           # Amount of data sent and received per minute
    LogErrorRate,           # Number of errors in message handling per minute
    LogResourceUtilization, # CPU and memory usage of the process 
    LogFPS):                # Frames per second of the game

    TIME_SYNC_INTERVAL = 300  # Time sync interval in seconds (5 minutes)

    def __init__(self):
        os.makedirs(LOGS_DIR, exist_ok=True)
        LogTransmissionTimes.__init__(self)
        LogDropoutRate.__init__(self)
        LogRealTimeViolations.__init__(self)
        LogThroughput.__init__(self)
        LogBandwidth.__init__(self)
        LogErrorRate.__init__(self)
        LogResourceUtilization.__init__(self)
        LogFPS.__init__(self)

        self.time_offset = timedelta(0)
        self.last_sync_time = None
        self.time_sync_thread = threading.Thread(target=self.synchronize_time_periodically, daemon=True)
        self.time_sync_thread.start()
        
        # Initial synchronization
        self.synchronize_time()

    def synchronize_time(self):
        external_time = self.get_time_timeapi_io()
        if external_time:
            self.time_offset = external_time - datetime.utcnow()
            self.last_sync_time = datetime.utcnow()

    def synchronize_time_periodically(self):
        while True:
            self.synchronize_time()
            time.sleep(self.TIME_SYNC_INTERVAL)

    def get_adjusted_time(self):
        # Use the offset to calculate the approximate current time
        return datetime.utcnow() + self.time_offset

    def on_message_sent(self, message: Message):
        message.send_timestamp = self.get_adjusted_time()
        self.increment_sent_message(message.id)
        self.increment_sent_throughput() 
        serialized_message = message.to_json()
        message_size = len(serialized_message.encode('utf-8'))
        self.add_bytes_sent(message_size)

    def on_message_received(self, message: Message):
        message.receive_timestamp = self.get_adjusted_time()
        self.increment_received_message(message.id)
        self.increment_received_throughput()

        if message.send_timestamp:
            transmission_time = (message.receive_timestamp - message.send_timestamp).total_seconds()
            self.transmission_times.put(transmission_time)
            if transmission_time > self.max_allowed_latency:
                self.increment_real_time_violations()

        serialized_message = message.to_json()
        message_size = len(serialized_message.encode('utf-8'))
        self.add_bytes_received(message_size)

    def get_time_timeapi_io(self, timezone='UTC'):
        url = f'https://timeapi.io/api/Time/current/zone?timeZone={timezone}'
        try:
            response = requests.get(url)
            data = response.json()
            hour = data['hour']
            minute = data['minute']
            second = data['seconds']
            millisecond = data['milliSeconds']
            current_time = datetime.utcnow().replace(hour=hour, minute=minute, second=second, microsecond=millisecond*1000)
            return current_time

        except Exception as e:
            print(f"Error fetching time: {e}")
            return None
