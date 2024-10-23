from matplotlib import pyplot as plt

class EEGVisualizer:
    def __init__(self, ch_names, picks):
        self.ch_names = ch_names
        self.picks = picks
        self.colors = ['r', 'g', 'b', 'c', 'm', 'y']  # Colors for the channels
        self.fig, self.ax = self.setup_plot()

    def setup_plot(self):
        """Set up the Matplotlib plot for the EEG channels."""
        plt.ion()  # Enable interactive mode for live plotting
        fig, ax = plt.subplots(6, 1, sharex=True, constrained_layout=True)
        return fig, ax

    def update_plot(self, ts, data):
        """Update the plot with new EEG data."""
        for axis in self.ax:
            axis.clear()  # Clear previous plot

        # Plot each channel's data
        for idx, data_channel in enumerate(data):
            self.ax[idx].plot(ts, data_channel, color=self.colors[idx])

        # Add titles and labels
        for idx, ch in enumerate(self.picks):
            self.ax[idx].set_title(f"EEG {ch}")
        self.ax[-1].set_xlabel("Timestamp (LSL time)")

        plt.pause(0.01)  # Pause to update the plot