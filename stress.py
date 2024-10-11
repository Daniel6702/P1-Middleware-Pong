import threading
import socket
import time
import sys
import argparse
import random
import string
import psutil

def cpu_stress(stop_event, cpu_threads):
    def cpu_task():
        while not stop_event.is_set():
            # Perform a meaningless computation
            _ = sum(i*i for i in range(10000))
    
    threads = []
    for _ in range(cpu_threads):
        t = threading.Thread(target=cpu_task)
        t.start()
        threads.append(t)
    
    return threads

def memory_stress(stop_event, memory_size_mb, allocation_interval=0.1):
    allocated_memory = []
    
    def memory_task():
        nonlocal allocated_memory
        try:
            while not stop_event.is_set():
                # Allocate memory in chunks (e.g., 10 MB)
                chunk_size = 10 * 1024 * 1024  # 10 MB
                chunk = bytearray(chunk_size)
                allocated_memory.append(chunk)
                print(f"Allocated {len(allocated_memory)*10} MB")
                time.sleep(allocation_interval)
        except MemoryError:
            print("Memory allocation failed due to insufficient memory.")
        except Exception as e:
            print(f"Memory stress thread encountered an error: {e}")
    
    t = threading.Thread(target=memory_task)
    t.start()
    
    return [t]

def network_stress(stop_event, target_host, target_port, connections, data_rate_kbps):
    def network_task(thread_id):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((target_host, target_port))
            print(f"Network thread {thread_id} connected to {target_host}:{target_port}")
            while not stop_event.is_set():
                # Generate random data to send
                data = ''.join(random.choices(string.ascii_letters + string.digits, k=1024)).encode('utf-8')
                s.sendall(data)
                # Control data rate
                time_per_kb = 1 / (data_rate_kbps / 8)  # seconds per KB
                time.sleep(time_per_kb)
        except Exception as e:
            print(f"Network stress thread {thread_id} encountered an error: {e}")
        finally:
            s.close()
            print(f"Network thread {thread_id} disconnected.")
    
    threads = []
    for i in range(connections):
        t = threading.Thread(target=network_task, args=(i+1,))
        t.start()
        threads.append(t)
    
    return threads

def main():
    parser = argparse.ArgumentParser(description="CPU, Memory, and Network Stress Tester")
    parser.add_argument('--cpu', type=int, default=4, help='Number of CPU stress threads (default: 4)')
    parser.add_argument('--memory', type=int, default=500, help='Amount of memory to allocate in MB (default: 500)')
    parser.add_argument('--network_host', type=str, default='127.0.0.1', help='Target host for network stress (default: 127.0.0.1)')
    parser.add_argument('--network_port', type=int, default=9999, help='Target port for network stress (default: 9999)')
    parser.add_argument('--connections', type=int, default=10, help='Number of simultaneous network connections (default: 10)')
    parser.add_argument('--data_rate', type=int, default=100, help='Data rate per connection in kbps (default: 100)')
    
    args = parser.parse_args()
    
    stop_event = threading.Event()
    
    print("Starting stress test...")
    print(f"CPU Threads: {args.cpu}")
    print(f"Memory Allocation: {args.memory} MB")
    print(f"Network Stress: {args.connections} connections at {args.data_rate} kbps each to {args.network_host}:{args.network_port}")
    
    # Start CPU stress
    cpu_threads = cpu_stress(stop_event, args.cpu)
    
    # Start Memory stress
    memory_threads = memory_stress(stop_event, args.memory)
    
    # Start Network stress
    network_threads = network_stress(stop_event, args.network_host, args.network_port, args.connections, args.data_rate)
    
    try:
        while True:
            # Monitor and display system stats
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            print(f"CPU Usage: {cpu_percent}% | Memory Usage: {memory.percent}%")
    except KeyboardInterrupt:
        print("\nStopping stress test...")
        stop_event.set()
    
    # Wait for all threads to finish
    for t in cpu_threads + memory_threads + network_threads:
        t.join()
    
    print("Stress test completed.")

if __name__ == "__main__":
    main()
