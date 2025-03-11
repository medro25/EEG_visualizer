import asyncio
import json
import logging
import websockets
from data.eeg_data_simulator import LSLDataSimulator
from data.lsl_stream_connector import LSLStreamConnector

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

class EEGWebSocketServer:
    def __init__(self, host="0.0.0.0", port=8765, bufsize=200):
        """Initialize WebSocket server for EEG streaming."""
        self.host = host
        self.port = port
        self.bufsize = bufsize
        self.simulator = LSLDataSimulator()
        self.connector = None  # Will be assigned when a stream is selected

    async def websocket_handler(self, websocket):  # ✅ `path` is required but unused
        """Handles WebSocket communication with the frontend."""
        logging.info("[WEBSOCKET] New client connected.")
       

        try:
            # Step 1: Search for available EEG streams
            print("\n🔍 Searching for LSL streams...\n")
            available_streams = self.simulator.find_streams()

            if not available_streams:
                await websocket.send(json.dumps({"error": "No streams available."}))
                return

            # Step 2: Send available streams to frontend
            stream_names = [stream.name() for stream in available_streams]
            print(f"\n✅ Available streams: {stream_names}\n")
            await websocket.send(json.dumps({"streams": stream_names}))

            # Step 3: Receive selected stream from frontend
            message = await websocket.recv()
            selected_stream_data = json.loads(message)  # Parse JSON

            selected_stream_name = selected_stream_data.get("stream_name")  # Extract the stream name
            print(f"\n🎯 Selected stream: {selected_stream_name}\n")

            # Step 4: Connect to the selected stream
            self.connector = LSLStreamConnector(bufsize=self.bufsize)
            if not self.connector.connect(selected_stream_name):
                await websocket.send(json.dumps({"error": "Failed to connect to stream."}))
                return

            logging.info(f"✅ Connected to {selected_stream_name}")

            # Step 5: Stream real-time EEG data
            await self.stream_real_time(websocket)

        except websockets.exceptions.ConnectionClosed as e:
            logging.warning(f"🛑 WebSocket connection closed: {e}")

        except Exception as e:
            logging.error(f"❌ WebSocket error: {e}")

    async def stream_real_time(self, websocket):
        """Continuously send EEG data over WebSocket."""
        interval = self.connector.bufsize / self.connector.sfreq if self.connector.sfreq else 0.1
        print("\n📡 Streaming EEG data to client...")

        try:
            while True:
                data, timestamps = self.connector.get_data(winsize=1)
                if data is not None:
                    message = {
                        "ch_names": self.connector.ch_names,
                        "timestamps": timestamps.tolist(),
                        "data": data.tolist(),
                        "winsize": 1
                    }
                    await websocket.send(json.dumps(message))
                    print("\n📡 Sent EEG data.\n")

                await asyncio.sleep(interval)

        except websockets.exceptions.ConnectionClosed:
            print("\n🛑 WebSocket connection closed.")
            self.connector.stream.disconnect()

    async def start_server(self):
        """Starts the WebSocket server correctly."""
        print(f"🚀 WebSocket server running on ws://{self.host}:{self.port}...")

        # ✅ Fix: Directly pass `websocket_handler` instead of using `lambda`
        server = await websockets.serve(self.websocket_handler, self.host, self.port)
        await server.wait_closed()

    def run(self):
        """Runs the WebSocket server."""
        print("\n🔹 Starting EEG WebSocket Server...\n")

        # ✅ Fix: Ensure correct event loop handling
        asyncio.run(self.start_server())

if __name__ == "__main__":
    eeg_server = EEGWebSocketServer()
    eeg_server.run()
