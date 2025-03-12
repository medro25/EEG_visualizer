import asyncio
import json
import logging
import websockets
import numpy as np
from data.eeg_data_simulator import LSLDataSimulator
from data.lsl_stream_connector import LSLStreamConnector

logging.basicConfig(level=logging.DEBUG)

class EEGWebSocketServer:
    def __init__(self, host="0.0.0.0", port=8765, bufsize=200):
        self.host = host
        self.port = port
        self.bufsize = bufsize
        self.simulator = LSLDataSimulator()
        self.connector = None  

    async def websocket_handler(self, websocket):
        logging.info("✅ [WebSocket] New client connected.")

        try:
            # ✅ Send available EEG streams
            available_streams = self.simulator.find_streams()
            if not available_streams:
                logging.warning("⚠️ No EEG streams found!")
                await websocket.send(json.dumps({"error": "No streams available."}))
                return

            stream_info = [{"name": stream.name(), "channels": []} for stream in available_streams]
            await websocket.send(json.dumps({"streams": stream_info}))

            # ✅ Receive stream selection
            message = await websocket.recv()
            selected_stream_data = json.loads(message)
            selected_stream_name = selected_stream_data.get("stream_name")

            if not selected_stream_name:
                logging.error("❌ Invalid stream name received.")
                await websocket.send(json.dumps({"error": "Invalid stream name."}))
                return

            # ✅ Connect to EEG stream
            self.connector = LSLStreamConnector(bufsize=self.bufsize)
            if not self.connector.connect(selected_stream_name):
                logging.error(f"❌ Failed to connect to stream: {selected_stream_name}")
                await websocket.send(json.dumps({"error": "Failed to connect to stream."}))
                return

            # ✅ Send available EEG channels
            await websocket.send(json.dumps({"channels": self.connector.ch_names}))

            # ✅ Receive selected channels
            message = await websocket.recv()
            selected_channels_data = json.loads(message)
            selected_channels = selected_channels_data.get("selected_channels", [])

            if not selected_channels or not set(selected_channels).issubset(self.connector.ch_names):
                logging.error("❌ Invalid channel selection.")
                await websocket.send(json.dumps({"error": "Invalid channel selection."}))
                return

            logging.info(f"✅ User selected channels: {selected_channels}")

            # ✅ Start streaming EEG data
            await self.stream_real_time(websocket, selected_channels)

        except websockets.exceptions.ConnectionClosed:
            logging.warning("🛑 WebSocket connection closed.")

        except Exception as e:
            logging.error(f"❌ WebSocket error: {e}")

    async def stream_real_time(self, websocket, selected_channels):
        interval = self.connector.bufsize / self.connector.sfreq if self.connector.sfreq else 0.1
        logging.info("📡 Streaming EEG data to client...")

        try:
            while True:
                data, timestamps = self.connector.get_data(winsize=1, picks=selected_channels)

                # ✅ Ensure valid data is received
                if data is None or timestamps is None or len(timestamps) == 0 or len(data) == 0:
                    logging.warning("⚠️ No valid EEG data received from the stream!")
                    continue

                # ✅ Convert to lists for JSON
                timestamps_list = timestamps.tolist() if isinstance(timestamps, np.ndarray) else list(timestamps)
                data_list = data.tolist() if isinstance(data, np.ndarray) else list(data)

                # ✅ Debug log EEG data samples before sending
                logging.info(f"⏳ First 5 Timestamps: {timestamps_list[:5]}")
                for i, ch in enumerate(selected_channels):
                    logging.info(f"📊 EEG Data Sample ({ch}): {data_list[i][:5]}")

                # ✅ Ensure data and timestamps lengths match
                if len(data_list[0]) != len(timestamps_list):
                    logging.error("❌ Mismatch between EEG data length and timestamps length!")
                    continue

                # ✅ Send EEG data over WebSocket
                message = {
                    "timestamps": timestamps_list,
                    "data": data_list,
                    "selected_channels": selected_channels
                }
                await websocket.send(json.dumps(message))
                logging.info("📡 Sent EEG data.")

                await asyncio.sleep(interval)

        except websockets.exceptions.ConnectionClosed:
            logging.warning("🛑 WebSocket connection closed.")
            self.connector.stream.disconnect()

    async def start_server(self):
        logging.info(f"🚀 WebSocket server running on ws://{self.host}:{self.port}...")
        async with websockets.serve(self.websocket_handler, self.host, self.port):
            await asyncio.Future()  # Keep running

    def run(self):
        logging.info("\n🔹 Starting EEG WebSocket Server...\n")
        asyncio.run(self.start_server())

if __name__ == "__main__":
    eeg_server = EEGWebSocketServer()
    eeg_server.run()
