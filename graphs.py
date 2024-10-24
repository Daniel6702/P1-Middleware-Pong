from plot_scripts.bandwidth import plot_bandwidth
from plot_scripts.fps import plot_fps
from plot_scripts.resources import plot_resource_usage
from plot_scripts.transmission_times import plot_transmission_times
from plot_scripts.throughput import plot_throughput
from plot_scripts.drop_rate import plot_drop_rates

if __name__ == "__main__":
    #plot_bandwidth(log_file='logs/bandwidth.log',output_image='plots/bandwidth_plot.png',show_plot=True)

    #plot_fps(log_file='logs/fps.log',output_image='plots/fps_plot.png',show_plot=True)

    #plot_resource_usage(log_file='logs/resources.log',output_image='plots/resource_usage_plot.png',show_plot=True)

    #plot_transmission_times(log_file='logs/transmission_times.log',output_image='plots/transmission_times_plot.png',show_plot=True,log_rate=None)

    #plot_throughput(log_file='logs/throughput.log',output_image='plots/throughput_plot.png',show_plot=True)
    log_files = [
        'logs/droprate1/dropout_rate1.log',
        'logs/droprate1/dropout_rate2.log',
        'logs/droprate1/dropout_rate3.log',
        'logs/droprate1/dropout_rate4.log'
    ]
    plot_drop_rates(log_files)