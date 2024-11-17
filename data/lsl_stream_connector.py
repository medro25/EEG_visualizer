import asyncio
import websockets
import json
from mne_lsl.stream import StreamLSL as Stream

class LSLStreamConnector:
    def __init__(self, bufsize, source_id, ch_names=None, sfreq=None):
        """
        Initialize the LSL Stream Connector.

        Parameters:
        - bufsize: Buffer size for the stream.
        - source_id: Source ID of the EEG data stream.
        - ch_names: List of channel names (optional).
        - sfreq: Sampling frequency of the EEG data (optional).
        """
        self.bufsize = bufsize
        self.source_id = source_id
        self.ch_names = ch_names  # Define default if necessary
        self.sfreq = sfreq  # Define default if necessary
        self.stream = None
        print(f"[INIT] LSLStreamConnector initialized with bufsize={self.bufsize} and source_id={self.source_id}")

    def connect(self):
        """Connect to an LSL stream and set default properties."""
        try:
            print("[CONNECT] Attempting to connect to LSL stream...")
            self.stream = Stream(bufsize=self.bufsize, source_id=self.source_id)
            #print("Print all attributes of the stream object",dir(self.stream))  # Print all attributes of the stream object
            
            self.stream.connect()
            print("[CONNECT] Successfully connected to LSL stream. Amine")
            
            # Set default `sfreq` and `ch_names` from the stream if not provided
            if self.sfreq is None:
                self.sfreq = self.stream.info["sfreq"]  # Example, replace as per stream property
                print(f"[CONNECT] Retrieved sfreq: {self.sfreq}")
            if self.ch_names is None:
                self.ch_names = self.stream.ch_names  # Example, replace as per stream property
                print(f"[CONNECT] Retrieved ch_names: {self.ch_names}")
                
        except Exception as e:
            print(f"[ERROR] Failed to connect to LSL stream: {e}")

    def get_data(self, winsize=None, picks=None):
        """
        Retrieve EEG data from the stream.

        Parameters:
        - winsize: Size of the window in seconds to retrieve data.
        - picks: Channels to pick for data retrieval.

        Returns:
        - data: EEG data for the specified window and channels.
        - ts: Timestamps for the retrieved data.
        """
        try:
            if not self.ch_names:
                raise AttributeError("ch_names attribute is not set.")
            if not self.sfreq:
                raise AttributeError("sfreq attribute is not set.")
            
            if picks is None:
                picks = self.ch_names[:6]  # Use ch_names passed from EEGDataSimulator
                #print("picks",picks)
            if winsize is None:
                winsize = self.stream.n_new_samples / self.sfreq  # Use sfreq passed from EEGDataSimulator
                #print("winsize",winsize)
            print(f"[GET DATA] Retrieving data with winsize={winsize} and picks={picks}")
            
            # Retrieve data and timestamps from the ring buffer
            data, ts = self.stream.get_data(winsize, picks=picks)
            print(f"[GET DATA] Retrieved data: {data[:10]}...")  # Print only the first 10 samples
            print(f"[GET DATA] Retrieved timestamps: {ts[:10]}...") 
            return data, ts
        
        except AttributeError as e:
            print(f"[ERROR] Attribute error in get_data (missing attribute): {e}")
        except ValueError as e:
            print(f"[ERROR] Value error in get_data (invalid input): {e}")
        except ConnectionError as e:
            print(f"[ERROR] Connection error in get_data: {e}")
        except Exception as e:
            print(f"[ERROR] Failed to retrieve data: {e}")
        except :
            print("nothing is wrong")
        return None, None

    def get_channel_types(self):
        """Get channel types from the stream."""
        try:
            print("[GET CHANNEL TYPES] Retrieving channel types from the stream...")
            channel_types = self.stream.get_channel_types(unique=True)
            print(f"[GET CHANNEL TYPES] Retrieved channel types: {channel_types}")
            return channel_types
        except Exception as e:
            print(f"[ERROR] Failed to retrieve channel types: {e}")
            return None

