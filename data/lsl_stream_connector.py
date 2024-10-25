import asyncio
import websockets
import json
from mne_lsl.stream import StreamLSL as Stream

class LSLStreamConnector:
    def __init__(self, bufsize, source_id):
        self.bufsize = bufsize
        self.source_id = source_id
        self.stream = None

    def connect(self):
        """Connect to an LSL stream."""
        self.stream = Stream(bufsize=self.bufsize, source_id=self.source_id)
        self.stream.connect()

    def get_data(self, winsize, picks):
        """Retrieve EEG data from the stream."""
        return self.stream.get_data(winsize, picks=picks)

    def get_channel_types(self):
        """Get channel types from the stream."""
        return self.stream.get_channel_types(unique=True)

    async def websocket_server(self, websocket, path):
        """Send data through the WebSocket."""
        self.connect()
        while True:
            data = self.get_data(500, picks=self.get_channel_types())
            await websocket.send(json.dumps(data.tolist()))
            await asyncio.sleep(1)
