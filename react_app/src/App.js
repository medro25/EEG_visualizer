import React, { useState, useEffect } from "react";

const App = () => {
  const [socket, setSocket] = useState(null);
  const [streams, setStreams] = useState([]);
  const [selectedStream, setSelectedStream] = useState("");
  const [eegData, setEegData] = useState([]);

  useEffect(() => {
    // Connect to WebSocket server
    const ws = new WebSocket("ws://localhost:8765");

    ws.onopen = () => {
      console.log("✅ Connected to WebSocket server");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("📩 Received from server:", data);

      if (data.streams) {
        setStreams(data.streams); // Save available streams
      }

      if (data.data) {
        setEegData(data); // Save EEG data
      }
    };

    ws.onerror = (error) => {
      console.error("❌ WebSocket error:", error);
    };

    ws.onclose = () => {
      console.log("🛑 WebSocket connection closed");
    };

    setSocket(ws);
    return () => ws.close(); // Cleanup WebSocket on component unmount
  }, []);

  const handleStreamSelect = (event) => {
    const streamName = event.target.value;
    setSelectedStream(streamName);
    
    if (socket && streamName) {
      socket.send(JSON.stringify({ stream_name: streamName }));
      console.log(`📤 Sent selected stream: ${streamName}`);
    }
  };

  return (
    <div>
      <h1>EEG Visualizer</h1>
      <label>Select EEG Stream:</label>
      <select value={selectedStream} onChange={handleStreamSelect}>
        <option value="">-- Choose a Stream --</option>
        {streams.map((stream, index) => (
          <option key={index} value={stream}>
            {stream}
          </option>
        ))}
      </select>

      <h2>EEG Data:</h2>
      {eegData.data ? (
        <pre>{JSON.stringify(eegData, null, 2)}</pre>
      ) : (
        <p>No EEG data yet.</p>
      )}
    </div>
  );
};

export default App;
