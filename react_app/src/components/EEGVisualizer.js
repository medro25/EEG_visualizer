// src/components/EEGVisualizer.js

import React, { useEffect, useState } from 'react';

const EEGVisualizer = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/api/eeg-data');
        const result = await response.json();
        setData(result);
      } catch (error) {
        console.error('Error fetching EEG data:', error);
      }
    };

    const intervalId = setInterval(fetchData, 1000); // Fetch data every second
    return () => clearInterval(intervalId); // Cleanup interval on unmount
  }, []);

  return (
    <div>
      {data ? (
        data.map((channelData, index) => (
          <div key={index}>
            <h3>Channel {index + 1}</h3>
            <pre>{JSON.stringify(channelData, null, 2)}</pre>
          </div>
        ))
      ) : (
        <p>Loading EEG data...</p>
      )}
    </div>
  );
};

export default EEGVisualizer;
