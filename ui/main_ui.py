from data.eeg_data_simulator import EEGDataSimulator
from data.lsl_stream_connector import LSLStreamConnector
from visualizer.eeg_visualizer import EEGVisualizer

class MainUI:
    def __init__(self):
        self.simulator = None
        self.stream_connector = None
        self.visualizer = None

    def start(self):
        """Start the EEG data visualization system."""
        # Step 1: Initialize and start EEG data simulator
        self.simulator = EEGDataSimulator()
        info, sfreq, n_channels, ch_names = self.simulator.start_stream()

        # Step 2: Connect to LSL stream
        self.stream_connector = LSLStreamConnector(bufsize=2, source_id=self.simulator.source_id)
        self.stream_connector.connect()

        # Step 3: Set up visualizer for the first 6 channels
        picks = ch_names[:6]  # Pick the first 6 channels
        self.visualizer = EEGVisualizer(ch_names, picks)

        # Step 4: Continuously retrieve and visualize data
        while True:
            winsize = self.stream_connector.stream.n_new_samples / sfreq
            data, ts = self.stream_connector.get_data(winsize, picks=picks)
            self.visualizer.update_plot(ts, data)
