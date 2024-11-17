import os
from pathlib import Path
import uuid
import time
from mne_lsl.datasets import sample
from mne_lsl.player import PlayerLSL as Player

class EEGDataSimulator:
    def __init__(self, chunk_size=200):
        self.chunk_size = chunk_size
        self.source_id = uuid.uuid4().hex
        self.player = None
        self.interval = None
        print(f"[DEBUG] Initialized EEGDataSimulator with chunk_size={self.chunk_size} and source_id={self.source_id}")

    def start_stream(self):
        """Simulates EEG stream."""
        print("[DEBUG] Starting EEG data stream...")
        
        # Define EEG data file path
        fname = sample.data_path() / "sample-ant-raw.fif"
        
        # Check if file already exists
        if not fname.is_file():
            print(f"[DEBUG] File not found at {fname}, downloading...")
            sample.data_path()  # This will download all necessary files if not present
        else:
            print(f"[DEBUG] File already exists at {fname}, skipping download.")

        # Initialize the Player with file and chunk settings
        self.player = Player(fname, chunk_size=self.chunk_size, source_id=self.source_id)
        self.player.start()
        print("[DEBUG] Player started successfully.")

        # Retrieve stream information
        info = self.player.info
        self.sfreq = info["sfreq"]  # Sampling frequency
        self.n_channels = len(info['ch_names'])  # Number of channels
        self.ch_names = info['ch_names']  # Channel names

        # Calculate interval between data pushes
        self.interval = self.chunk_size / self.sfreq
        print(f"[DEBUG] Streaming data at {self.sfreq} Hz with {self.n_channels} channels.")
        print(f"[DEBUG] Interval between push operations: {self.interval:.6f} seconds.")
        
        # Debug information
        print(f"[DEBUG] Stream Info: {info}")
        print(f"[DEBUG] Sampling Frequency: {self.sfreq} Hz")
        print(f"[DEBUG] Number of Channels: {self.n_channels}")
        print(f"[DEBUG] Channel Names: {self.ch_names}")
        
        return info, self.sfreq, self.n_channels, self.ch_names

    def stream_data(self):
        """Stream EEG data at intervals defined by self.interval."""
        while True:
            # Generate or retrieve a chunk of data
            data = self.player.get_data()
            print(f"[DEBUG] Streaming data: {data}")
            
            # Wait for the calculated interval before the next push
            time.sleep(self.interval)

# Testing the class
if __name__ == "__main__":
    simulator = EEGDataSimulator(chunk_size=200)
    stream_info, sfreq, n_channels, ch_names = simulator.start_stream()
    print("[TEST] Stream information retrieved successfully.")
