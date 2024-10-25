import React, { useEffect, useState } from 'react';
import * as d3 from 'd3';

const EEGVisualizer = () => {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8765');
    
    socket.onmessage = function (event) {
      const newData = JSON.parse(event.data);
      setData(newData);  // Set data received from WebSocket
    };

    return () => socket.close();
  }, []);

  useEffect(() => {
    // D3 visualization logic
    if (data.length > 0) {
      const svg = d3.select("#eeg-plot")
        .attr("width", 800)
        .attr("height", 400);
      
      svg.selectAll("*").remove();  // Clear previous plots

      data.forEach((channelData, idx) => {
        const line = d3.line()
          .x((d, i) => i)
          .y(d => d)
          .curve(d3.curveMonotoneX);

        svg.append("path")
          .datum(channelData)
          .attr("fill", "none")
          .attr("stroke", "blue")
          .attr("stroke-width", 1.5)
          .attr("d", line);
      });
    }
  }, [data]);

  return <svg id="eeg-plot"></svg>;
};

export default EEGVisualizer;
