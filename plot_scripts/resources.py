import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os
from typing import Optional

def plot_resource_usage(
    log_file: str = 'logs/resource_usage.log',
    output_image: str = 'plots/resource_usage_plot.png',
    show_plot: bool = True
) -> Optional[plt.Figure]:
    """
    Reads CPU and memory usage data from a log file and plots them over time.

    Parameters:
    - log_file (str): Path to the resource usage log file.
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
    # Assuming the log file has no header
    column_names = ['timestamp', 'cpu_percent', 'memory_usage_mb']
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
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # Plot CPU Usage
    color_cpu = 'tab:red'
    ax1.set_xlabel('Time', fontsize=14)
    ax1.set_ylabel('CPU Usage (%)', color=color_cpu, fontsize=14)
    ax1.plot(
        data.index,
        data['cpu_percent'],
        label='CPU Usage (%)',
        color=color_cpu,
        marker='o',
        linestyle='-'
    )
    ax1.tick_params(axis='y', labelcolor=color_cpu)

    # Create a second y-axis for Memory Usage
    ax2 = ax1.twinx()
    color_mem = 'tab:blue'
    ax2.set_ylabel('Memory Usage (MB)', color=color_mem, fontsize=14)
    ax2.plot(
        data.index,
        data['memory_usage_mb'],
        label='Memory Usage (MB)',
        color=color_mem,
        marker='x',
        linestyle='--'
    )
    ax2.tick_params(axis='y', labelcolor=color_mem)

    # Combine legends from both axes
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper left', fontsize=12)

    # Beautify the plot
    plt.title('CPU and Memory Usage Over Time', fontsize=18)
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Improve date formatting on the x-axis
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax1.xaxis.set_major_locator(mdates.AutoDateLocator())

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
    return fig
