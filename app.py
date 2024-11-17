import asyncio
import websockets
import json
import logging
from data.lsl_stream_connector import LSLStreamConnector
from data.eeg_data_simulator import EEGDataSimulator
from visualizer.eeg_visualizer import EEGVisualizer
from mne import set_log_level

logging.basicConfig(level=logging.DEBUG)

class EEGWebSocketServer:
    def __init__(self, host, port, bufsize=2, chunk_size=200):
        self.host = host
        self.port = port
        self.chunk_size = chunk_size
        self.bufsize = bufsize
        self.simulator = None
        self.connector = None
        self.visualizer = None

    def initialize_simulator(self):
        """Initialize the EEG data simulator."""
        logging.debug("[DEBUG] Initializing EEG Data Simulator")
        set_log_level("WARNING")
        self.simulator = EEGDataSimulator(chunk_size=self.chunk_size)
        info, sfreq, n_channels, ch_names = self.simulator.start_stream()

        if info is None:
            logging.error("[ERROR] Failed to initialize EEG data stream. Exiting...")
            exit(1)

        # Retrieve the unique source ID for the stream
        source_id = self.simulator.source_id
        
        # Initialize LSL Stream Connector with the simulator's source ID
        self.connector = LSLStreamConnector(bufsize=self.bufsize, source_id=source_id)
        self.connector.connect()
        
        # Dynamically calculate `winsize` and `picks`
        self.sfreq = sfreq  # Sampling frequency from the simulator
        self.picks = ch_names[:6]  # Select the first 6 channels or adapt as needed
        self.winsize = self.connector.stream.n_new_samples / self.sfreq
        self.visualizer = EEGVisualizer(ch_names=self.picks, picks=self.picks)
        logging.debug(f"[DEBUG] Calculated picks: {self.picks}")
        logging.debug(f"[DEBUG] Calculated winsize: {self.winsize}")

    async def websocket_handler(self, websocket, path):
        """Handles WebSocket connections and sends EEG data to clients."""
        logging.debug("[DEBUG] WebSocket connection established")
        while True:
            try:
                self.winsize = self.connector.stream.n_new_samples / self.sfreq
                logging.debug(f"[DEBUG] Calculated winsize here: {self.winsize}") 
                
                # Retrieve EEG data using dynamically calculated winsize and picks
                eeg_data, timestamps = self.connector.get_data(winsize=self.winsize, picks=self.picks)
                
                if eeg_data is not None:
                    logging.debug("[DEBUG] Sending EEG data over WebSocket")
                    message = {
                        "timestamp": timestamps.tolist(),
                        "data": eeg_data.tolist(),
                        "ch_names": self.picks,  # Send channel names
                        "winsize": self.winsize  # Send window size
                    }
                    await websocket.send(json.dumps(message))  # Send the EEG data as JSON
                    logging.info("[INFO] EEG data sent successfully")
                    
                    # Update backend visualizer with data
                    self.visualizer.update_plot(ts=timestamps, data=eeg_data)
                    logging.debug("[DEBUG] Visualizer updated with new data")
                else:
                    logging.warning("[WARNING] No data to send, skipping this interval")
                
                await asyncio.sleep(0.1)  # Short pause between transmissions
            except Exception as e:
                logging.error(f"[ERROR] Error in WebSocket handler: {e}")
                break

    async def start_server(self):
        """Starts the WebSocket server and confirms it's running."""
        logging.debug(f"[DEBUG] Starting WebSocket server on ws://{self.host}:{self.port}")
        try:
            server = await websockets.serve(self.websocket_handler, self.host, self.port)
            logging.info(f"[INFO] WebSocket server successfully started on ws://{self.host}:{self.port}")
            while True:
                logging.info("[INFO] WebSocket server is running...")
                await asyncio.sleep(5)  # Log every 5 seconds to confirm the server is running
                if server.is_serving():
                    logging.info("[INFO] Server is actively serving connections.")
                else:
                    logging.warning("[WARNING] Server stopped serving; no connections are active.")
            await server.wait_closed()
        except Exception as e:
            logging.error(f"[ERROR] Failed to start WebSocket server: {e}")

    def run(self):
        """Initializes the simulator and runs the WebSocket server."""
        self.initialize_simulator()
        asyncio.run(self.start_server())

# Main entry point
if __name__ == "__main__":
    # Define server parameters
    HOST = "0.0.0.0"
    PORT = 8765

    # Initialize and run the WebSocket server
    eeg_server = EEGWebSocketServer(host=HOST, port=PORT)
    eeg_server.run()
