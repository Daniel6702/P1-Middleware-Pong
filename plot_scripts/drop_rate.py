import matplotlib.pyplot as plt

def plot_drop_rates(log_files):
    """
    Plots the drop rate of messages for a pong multiplayer game from a list of log files.
    
    Parameters:
    log_files (list): List of paths to log files.
    """
    
    for log_file in log_files:
        # Initialize lists to store data
        sent_msgs = []
        received_msgs = []
        
        # Read data from log file
        with open(log_file, 'r') as f:
            for line in f:
                if line.strip():  # Skip empty lines
                    time_str, sent_str, received_str = line.strip().split(',')
                    sent_msgs.append(int(sent_str))
                    received_msgs.append(int(received_str))
        
        # Compute average 'sent' and 'received' per interval
        total_sent = sum(sent_msgs)
        total_received = sum(received_msgs)
        num_intervals = len(sent_msgs)
        avg_sent = total_sent / num_intervals
        avg_received = total_received / num_intervals
        
        # Calculate the expected ratio of received to sent messages
        expected_ratio = avg_received / avg_sent if avg_sent else 0
        
        # Compute drop rate per interval
        drop_rates = []
        for sent, received in zip(sent_msgs, received_msgs):
            expected_received = expected_ratio * sent
            if expected_received > 0:
                drop_rate = (expected_received - received) / expected_received
            else:
                drop_rate = 0
            drop_rates.append(drop_rate)
        
        # Plot drop rates over interval indices
        intervals = range(len(drop_rates))
        plt.plot(intervals, drop_rates, label=log_file)
    
    plt.xlabel('Interval')
    plt.ylabel('Drop Rate')
    plt.title('Message Drop Rate Over Time')
    plt.legend()
    plt.grid(True)
    plt.show()