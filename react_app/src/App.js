import React, { useState, useEffect, useRef } from "react";
import EEGGraph from "./components/EEGGraph";
//import EEGVisualizer from "./components/EEGVisualizer";

const App = () => {
  const [socket, setSocket] = useState(null);
  const [streams, setStreams] = useState([]);
  const [selectedStream, setSelectedStream] = useState("");
  const [channels, setChannels] = useState([]);
  const [selectedChannels, setSelectedChannels] = useState([]);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8765");

    ws.onopen = () => console.log("✅ Connected to WebSocket server");

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log("📩 Received from server:", data);

        if (data.streams) setStreams(data.streams);
        if (data.channels) setChannels(data.channels);
      } catch (error) {
        console.error("❌ Error parsing WebSocket message:", error);
      }
    };

    ws.onerror = (error) => console.error("❌ WebSocket error:", error);
    ws.onclose = () => console.log("🛑 WebSocket connection closed");

    setSocket(ws);
    return () => ws.close();
  }, []);

  const handleStreamSelect = (event) => {
    const streamName = event.target.value;
    setSelectedStream(streamName);
    setSelectedChannels([]);

    if (socket && streamName) {
      socket.send(JSON.stringify({ stream_name: streamName }));
      console.log(`📤 Sent selected stream: ${streamName}`);
    }
  };

  const handleChannelToggle = (channel) => {
    const updatedChannels = selectedChannels.includes(channel)
      ? selectedChannels.filter((ch) => ch !== channel)
      : [...selectedChannels, channel];

    setSelectedChannels(updatedChannels);

    if (socket) {
      socket.send(JSON.stringify({ selected_channels: updatedChannels }));
      console.log(`📤 Sent selected channels: ${updatedChannels}`);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>EEG Visualizer</h1>

      <div style={{ display: "flex", gap: "20px", alignItems: "center" }}>
        <div>
          <label><strong>Select EEG Stream:</strong></label>
          <select value={selectedStream} onChange={handleStreamSelect} style={{ padding: "5px", width: "200px" }}>
            <option value="">-- Choose a Stream --</option>
            {streams.map((stream, index) => (
              <option key={index} value={stream.name}>{stream.name}</option>
            ))}
          </select>
        </div>

        {channels.length > 0 && (
          <div ref={dropdownRef} style={{ position: "relative" }}>
            <label><strong>Select EEG Channels:</strong></label>
            <div className="dropdown-header" 
              onClick={() => setDropdownOpen(!dropdownOpen)}
              style={{ padding: "8px", border: "1px solid #ccc", cursor: "pointer", backgroundColor: "#f9f9f9", width: "200px", borderRadius: "5px", textAlign: "left" }}>
              {selectedChannels.length > 0 ? selectedChannels.join(", ") : "Select Channels"}
            </div>
            
            {dropdownOpen && (
              <div className="dropdown-menu" style={{ position: "absolute", top: "100%", left: 0, backgroundColor: "#fff", border: "1px solid #ccc", width: "200px", maxHeight: "150px", overflowY: "auto", borderRadius: "5px", zIndex: 1000 }}>
                {channels.map((channel, index) => (
                  <label key={index} style={{ display: "block", padding: "5px", cursor: "pointer" }}>
                    <input type="checkbox" value={channel} checked={selectedChannels.includes(channel)} onChange={() => handleChannelToggle(channel)} />{" "}
                    {channel}
                  </label>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      <EEGGraph wsUrl="ws://localhost:8765" selectedChannels={selectedChannels} />
      {/* <EEGVisualizer wsUrl="ws://localhost:8765" selectedChannels={selectedChannels} /> */}
    </div>
  );
};

export default App;
