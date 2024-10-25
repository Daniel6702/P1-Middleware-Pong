import matplotlib.pyplot as plt
import numpy as np


def compress_array(arr, chunk_size):
    # Ensure the array length is a multiple of the chunk_size by trimming excess elements
    trimmed_length = len(arr) - (len(arr) % chunk_size)
    trimmed_arr = arr[:trimmed_length]

    # Reshape the array to create chunks of size chunk_size
    reshaped_arr = trimmed_arr.reshape(-1, chunk_size)

    # Calculate the mean of each chunk
    compressed_arr = reshaped_arr.mean(axis=1)

    return compressed_arr

def plot_drop_rates(log_files):
    """
    Plots the drop rate of messages for a pong multiplayer game from a list of log files.
    
    Parameters:
    log_files (list): List of paths to log files.
    """
    
    for i in range(len(log_files)):
        # Initialize lists to store data
        sent_msgs = []
        received_msgs = []

        # Get the sent data from peer 1
        with open(log_files[i], 'r') as f:
            for line in f:
                if line.strip():
                    _, sent_str, _ = line.strip().split(',')
                    sent_msgs.append(int(sent_str))

        # Get the received data from peer 2
        with open(log_files[-i + 1], 'r') as f:
            for line in f:
                if line.strip():
                    _, _, received_str = line.strip().split(',')
                    received_msgs.append(int(received_str))

        # Compute drop rate per interval
        drop_rates = []
        for sent, received in zip(sent_msgs, received_msgs):
            drop_rate = (sent - received) / sent
            drop_rates.append(drop_rate)

        print(sum(drop_rates) / len(drop_rates))
        avg_drop_rates = compress_array(np.array(drop_rates), chunk_size=5)

        # Plot drop rates over interval indices
        intervals = range(len(avg_drop_rates))
        plt.plot(intervals, avg_drop_rates, label=f"Peer {i+1}")
    
    plt.xlabel('Interval')
    plt.ylabel('Drop Rate')
    plt.title('Message Drop Rate Over Time')
    plt.legend()
    plt.grid(True)
    plt.show()