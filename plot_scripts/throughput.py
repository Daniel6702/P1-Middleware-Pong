import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os
from typing import Optional

def plot_throughput(
    log_file: str = 'logs/throughput.log',
    output_image: str = 'plots/throughput_plot.png',
    show_plot: bool = True
) -> Optional[plt.Figure]:
    """
    Reads throughput data from a log file and plots sent and received throughput over time.

    Parameters:
    - log_file (str): Path to the throughput log file.
    - output_image (str): Path where the plot image will be saved.
    - show_plot (bool): Whether to display the plot interactively.

    Returns:
    - plt.Figure: The matplotlib figure object if plotting is successful.
    - None: If an error occurs during processing.
    """
    # Check if the log file exists
    if not os.path.exists(log_file):
        print(f"Error: The file '{log_file}' does not exist.")
        return None

    # Read the data into a pandas DataFrame
    # Assuming the log file has no header and format: timestamp,sent,received
    column_names = ['timestamp', 'sent', 'received']
    try:
        data = pd.read_csv(log_file, names=column_names)
    except Exception as e:
        print(f"Error reading the log file: {e}")
        return None

    # Convert UNIX timestamp to datetime
    try:
        data['datetime'] = pd.to_datetime(data['timestamp'], unit='s')
    except Exception as e:
        print(f"Error converting timestamps: {e}")
        return None

    # Set datetime as the index
    data.set_index('datetime', inplace=True)

    # Drop the original timestamp column
    data.drop('timestamp', axis=1, inplace=True)

    # Ensure the output directory exists
    plot_dir = os.path.dirname(output_image)
    if plot_dir and not os.path.exists(plot_dir):
        try:
            os.makedirs(plot_dir)
            print(f"Created directory '{plot_dir}' for output images.")
        except Exception as e:
            print(f"Error creating directory '{plot_dir}': {e}")
            return None

    # Plotting
    plt.figure(figsize=(14, 7))
    plt.plot(
        data.index,
        data['sent'],
        label='Sent Throughput',
        color='blue',
        marker='o',
        linestyle='-'
    )
    plt.plot(
        data.index,
        data['received'],
        label='Received Throughput',
        color='green',
        marker='x',
        linestyle='--'
    )

    # Beautify the plot
    plt.title('Sent and Received Throughput Over Time', fontsize=18)
    plt.xlabel('Time', fontsize=14)
    plt.ylabel('Throughput (packages per 10 seconds)', fontsize=14)  # Replace 'units' with actual units if known
    plt.legend(fontsize=12)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Improve date formatting on the x-axis
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())

    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot as an image file
    try:
        plt.savefig(output_image, dpi=300)
        print(f"Plot saved successfully at '{output_image}'.")
    except Exception as e:
        print(f"Error saving the plot: {e}")
        return None

    # Display the plot if requested
    if show_plot:
        plt.show()

    # Return the figure object
    return plt.gcf()

# Example usage:
if __name__ == "__main__":
    plot_throughput(
        log_file='logs/throughput.log',
        output_image='plots/throughput_plot.png',
        show_plot=True
    )
