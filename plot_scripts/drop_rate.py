import matplotlib.pyplot as plt

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

        # Plot drop rates over interval indices
        intervals = range(len(drop_rates))
        plt.plot(intervals[1:], drop_rates[1:], label=f"Peer {i+1}")
    
    plt.xlabel('Interval')
    plt.ylabel('Drop Rate')
    plt.title('Message Drop Rate Over Time')
    plt.legend()
    plt.grid(True)
    plt.show()