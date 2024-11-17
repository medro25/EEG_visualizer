import React, { useEffect, useState } from 'react';
import * as d3 from 'd3';

const EEGVisualizer = () => {
  const [data, setData] = useState([]);
  const [timestamps, setTimestamps] = useState([]);
  const [chNames, setChNames] = useState([]);
  const [winsize, setWinsize] = useState(0);

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8765');
    console.log("[WebSocket] Connecting to WebSocket...");

    socket.onmessage = function (event) {
      const message = JSON.parse(event.data);
      console.log("[WebSocket] Received new data:", message);

      setData(message.data);
      setTimestamps(message.timestamp);
      setChNames(message.ch_names);  // Set the channel names received
      setWinsize(message.winsize);    // Set the winsize received
    };

    socket.onopen = () => console.log("[WebSocket] Connection opened.");
    socket.onclose = () => console.log("[WebSocket] Connection closed.");

    return () => {
      console.log("[WebSocket] Closing WebSocket connection...");
      socket.close();
    };
  }, []);

  useEffect(() => {
    if (data.length > 0) {
      const svg = d3.select("#eeg-plot")
        .attr("width", 800)
        .attr("height", 400);
      
      svg.selectAll("*").remove();

      data.forEach((channelData, idx) => {
        const line = d3.line()
          .x((d, i) => i * (winsize / data[idx].length))  // Adjust x scale using winsize
          .y(d => d)
          .curve(d3.curveMonotoneX);

        svg.append("path")
          .datum(channelData)
          .attr("fill", "none")
          .attr("stroke", "blue")
          .attr("stroke-width", 1.5)
          .attr("d", line);

        svg.append("text")  // Add channel name labels
          .attr("x", 10)
          .attr("y", idx * 20 + 15)
          .style("font-size", "12px")
          .text(chNames[idx]);
      });
    }
  }, [data, chNames, winsize]);

  return <svg id="eeg-plot"></svg>;
};

export default EEGVisualizer;
