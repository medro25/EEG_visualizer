import React, { useEffect, useRef, useState } from "react";
import * as d3 from "d3";

const EEGVisualizer = ({ wsUrl, selectedChannels }) => {
  const svgRef = useRef();
  const [ws, setWs] = useState(null);

  useEffect(() => {
    const socket = new WebSocket(wsUrl);
    setWs(socket);

    console.log("🔄 [WebSocket] Connecting to WebSocket...");

    socket.onopen = () => console.log("✅ [WebSocket] Connection established.");
    
    socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        console.log("📩 [WebSocket] EEG Visualizer - Received Data:", message);

        if (!message.timestamps || !message.data || !message.selected_channels) {
            console.warn("⚠️ Missing EEG data fields:", message);
            return;
        }

        console.log("⏱️ Timestamps:", message.timestamps.length);
        console.log("📊 Data Received for Channels:", message.selected_channels);
        console.log("📊 Data Length for Each Channel:", message.data.map(d => d.length));

        if (message.selected_channels.length !== message.data.length) {
            console.error("❌ Mismatch: Number of channels does not match data received!");
            return;
        }

        // ✅ Pass `svgRef` to `updatePlot`
        updatePlot(svgRef, message.timestamps, message.data, message.selected_channels);

      } catch (error) {
        console.error("❌ [WebSocket] Error processing message:", error);
      }
    };

    socket.onclose = () => {
      console.warn("🛑 [WebSocket] Connection closed.");
      setTimeout(() => {
        console.log("🔄 [WebSocket] Reconnecting...");
        setWs(new WebSocket(wsUrl));
      }, 3000);
    };

    socket.onerror = (error) => console.error("❌ [WebSocket] Error:", error);

    return () => {
      console.log("🔌 [WebSocket] Closing connection...");
      socket.close();
    };
  }, [wsUrl, selectedChannels]);

  return <svg ref={svgRef} width={800} height={400}></svg>;
};

// ✅ Fix: Pass `svgRef` as a parameter
const updatePlot = (svgRef, timestamps, data, selectedChannels) => {
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove(); // Clear previous plots

    const width = 800, height = 400;
    const xScale = d3.scaleLinear().domain([0, timestamps.length]).range([0, width]);
    const yScale = d3.scaleLinear().domain([-1, 1]).range([height, 0]);

    selectedChannels.forEach((chName, index) => {
        const line = d3.line()
            .x((_, i) => xScale(i))
            .y(d => yScale(d))
            .curve(d3.curveMonotoneX);

        svg.append("path")
            .datum(data[index] || []) // Select correct data for each channel
            .attr("fill", "none")
            .attr("stroke", index % 2 === 0 ? "blue" : "red") // Different colors for each channel
            .attr("stroke-width", 1.5)
            .attr("d", line);
    });

    console.log("📊 EEG Data Successfully Plotted!");
};

export default EEGVisualizer;
