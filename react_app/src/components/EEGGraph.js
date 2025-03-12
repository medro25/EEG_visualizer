import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from "chart.js";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const EEGGraph = ({ wsUrl, selectedChannels }) => {
  const [data, setData] = useState({});
  const [timestamps, setTimestamps] = useState([]);
  const [winsize, setWinsize] = useState(0);
 

  useEffect(() => {
    const socket = new WebSocket(wsUrl);

    socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        console.log("📩 [WebSocket] Received EEG Data:", message);

        if (!message || !message.selected_channels || !message.data || !message.timestamps || !message.winsize) {
          console.warn("⚠️ Missing EEG data fields:", message);
          return;
        }

        console.log("⏱️ Received Timestamps:", message.timestamps);
        console.log("📊 Received EEG Data Before Scaling:", message.data);

        setWinsize(message.winsize);

        // ✅ Scale EEG data for better visibility
        const newData = {};
        message.selected_channels.forEach((ch, index) => {
          newData[ch] = message.data[index] || [];
        });

        console.log("📊 Scaled EEG Data Sample:", newData[selectedChannels[0]]?.slice(0, 10)); // ✅ Check first 10 values

        setData(newData);
        setTimestamps([...message.timestamps]);
      } catch (error) {
        console.error("❌ [WebSocket] Error parsing message:", error);
      }
    };

    return () => socket.close();
  }, [wsUrl, selectedChannels]);

  return (
    <div>
      <h2>Real-Time EEG Data</h2>
      {selectedChannels.map((chName, idx) => {
        const minVal = Math.min(...(data[chName] || [0]));
        const maxVal = Math.max(...(data[chName] || [0]));

        return (
          <div key={idx} style={{ width: "100%", height: "300px", marginBottom: "20px" }}>
            <h3>{chName}</h3>
            <Line 
              data={{ 
                labels: timestamps.length > 0 ? timestamps.map(t => t.toFixed(2)) : Array(10).fill(""),
                datasets: [{ 
                  label: chName, 
                  data: data[chName] ? data[chName] : Array(10).fill(0),
                  borderColor: "blue", 
                  borderWidth: 1.5 
                }]
              }} 
              options={{
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                  x: { title: { display: true, text: "Timestamp (LSL Time)" } },
                  y: { title: { display: true, text: "Amplitude" } },
                },
                }
              }
            />
          </div>
        );
      })}
    </div>
  );
};

export default EEGGraph;
