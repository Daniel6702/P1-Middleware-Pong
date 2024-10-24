import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from typing import Optional

def plot_transmission_times(
    log_file: str = 'logs/transmission_times.log',
    output_image: str = 'plots/transmission_times_plot.png',
    show_plot: bool = True,
    log_rate: Optional[float] = None
) -> Optional[plt.Figure]:
    """
    Reads transmission times from a log file and plots them over time or sequence,
    including an average transmission time line.
    
    Parameters:
    - log_file (str): Path to the transmission times log file.
    - output_image (str): Path where the plot image will be saved.
    - show_plot (bool): Whether to display the plot interactively.
    - log_rate (Optional[float]): Time interval (in seconds) between logged transmission times.
                                  If provided, timestamps will be inferred based on this rate.
                                  If None, the x-axis will represent the sequence index.

    Returns:
    - plt.Figure: The matplotlib figure object if plotting is successful.
    - None: If an error occurs during processing.
    """
    # Check if the log file exists
    if not os.path.exists(log_file):
        print(f"Error: The file '{log_file}' does not exist.")
        return None

    # Read the data into a pandas DataFrame
    # Assuming the log file has one transmission time per line without header
    try:
        data = pd.read_csv(log_file, header=None, names=['transmission_time'])
    except Exception as e:
        print(f"Error reading the log file: {e}")
        return None

    # Assign timestamps if log_rate is provided
    if log_rate is not None:
        # Create a datetime index starting from a base time (e.g., current time minus total duration)
        num_entries = len(data)
        total_duration = num_entries * log_rate
        base_time = pd.Timestamp.now() - pd.Timedelta(seconds=total_duration)
        data['datetime'] = base_time + pd.to_timedelta(data.index * log_rate, unit='s')
        data.set_index('datetime', inplace=True)
    else:
        # Use sequence index as x-axis
        data['index'] = data.index
        data.set_index('index', inplace=True)

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
        data['transmission_time'],
        label='Transmission Time (s)',
        color='purple',
        marker='o',
        linestyle='-'
    )

    # Calculate and plot the average transmission time
    average_time = data['transmission_time'].mean()
    plt.axhline(
        y=average_time,
        color='red',
        linestyle='--',
        linewidth=2,
        label=f'Average Transmission Time ({average_time:.2f} s)'
    )

    # Beautify the plot
    plt.title('Transmission Times Over Time', fontsize=18)
    plt.xlabel('Time' if log_rate else 'Sequence', fontsize=14)
    plt.ylabel('Transmission Time (s)', fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Improve date formatting on the x-axis if timestamps are used
    if log_rate is not None:
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
