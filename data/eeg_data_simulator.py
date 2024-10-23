import uuid
from mne_lsl.datasets import sample
from mne_lsl.player import PlayerLSL as Player

class EEGDataSimulator:
    def __init__(self, chunk_size=200):
        self.chunk_size = chunk_size
        self.source_id = uuid.uuid4().hex
        self.player = None

    def start_stream(self):
        """Simulates EEG stream."""
        fname = sample.data_path() / "sample-ant-raw.fif"
        self.player = Player(fname, chunk_size=self.chunk_size, source_id=self.source_id)
        self.player.start()

        # Get stream information
        info = self.player.info
        sfreq = info["sfreq"]  # Sampling frequency
        n_channels = len(info['ch_names'])  # Number of channels
        ch_names = info['ch_names']  # Channel names
        
        return info, sfreq, n_channels, ch_names
