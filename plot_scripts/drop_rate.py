import matplotlib.pyplot as plt
import numpy as np

def find_closest_data_point(data, target_timestamp, window=5):
    """
    Find the closest data point within the time window.
    :param data: List of data points with 'timestamp', 'sent', and 'received'.
    :param target_timestamp: The timestamp to align with.
    :param window: Time window (in seconds) for considering close timestamps.
    :return: The closest data point within the time window, or None if not found.
    """
    closest_point = None
    min_time_diff = window
    for entry in data:
        time_diff = abs(entry['timestamp'] - target_timestamp)
        if time_diff <= window and time_diff < min_time_diff:
            closest_point = entry
            min_time_diff = time_diff
    return closest_point

def plot_drop_rate(log_files, time_window=5):
    # Number of computers
    N = len(log_files)

    # Read data from each log file
    logs_data = []
    for log_file in log_files:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            data = []
            for line in lines:
                timestamp_str, sent_str, received_str = line.strip().split(',')
                timestamp = float(timestamp_str)
                sent = int(sent_str)
                received = int(received_str)
                data.append({'timestamp': timestamp, 'sent': sent, 'received': received})
            logs_data.append(data)
    
    # Reference to the first log file timestamps
    reference_data = logs_data[0]
    timestamps = []
    drop_rates = []
    
    # Compute drop rate at each time point (using reference log timestamps)
    for ref_entry in reference_data:
        ref_timestamp = ref_entry['timestamp']
        total_sent = ref_entry['sent']
        total_received = ref_entry['received']
        
        # Find the closest points in other logs based on the reference timestamp
        for log_data in logs_data[1:]:
            closest_entry = find_closest_data_point(log_data, ref_timestamp, window=time_window)
            if closest_entry:
                total_sent += closest_entry['sent']
                total_received += closest_entry['received']
        
        # Use the reference timestamp for plotting
        timestamps.append(ref_timestamp)
        
        # Expected total received messages in a fully connected network
        expected_total_received = total_sent * (N - 1)
        
        # Compute drop rate
        if expected_total_received > 0:
            drop_rate = (expected_total_received - total_received) / expected_total_received * 100
        else:
            drop_rate = 0
        drop_rates.append(drop_rate)
        print(sum(drop_rate))
    
    # Plot the drop rate over time
    plt.figure()
    plt.plot(timestamps, drop_rates, marker='o')
    plt.xlabel('Time')
    plt.ylabel('Drop Rate (%)')
    plt.title('Drop Rate Over Time (with Time Window Adjustment)')
    plt.grid(True)
    plt.show()

