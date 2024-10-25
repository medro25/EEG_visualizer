from data.lsl_stream_connector import LSLStreamConnector
from data.eeg_data_simulator import EEGDataSimulator
import asyncio
import websockets

async def websocket_handler(websocket, path, connector):
    while True:
        eeg_data = connector.get_data(winsize=2, picks=connector.get_channel_types())
        await websocket.send(str(eeg_data))

if __name__ == "__main__":
    simulator = EEGDataSimulator(chunk_size=200)
    info, sfreq, n_channels, ch_names = simulator.start_stream()
    source_id = simulator.source_id

    connector = LSLStreamConnector(bufsize=2, source_id=source_id)
    connector.connect()

    # Bind to '0.0.0.0' to make it accessible from all network interfaces
    start_server = websockets.serve(lambda ws, path: websocket_handler(ws, path, connector), "0.0.0.0", 8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
