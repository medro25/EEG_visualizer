import React from 'react';
import './App.css';
import WebSocketComponent from './components/WebSocketComponent';
import EEGGraph from './components/EEGGraph';



function App() {
  return (
    <div className="App">
      <h1>EEG Data Visualizer</h1>
      <WebSocketComponent/>
      {/* <EEGGraph wsUrl="ws://localhost:8765" /> */}
    </div>
  );
}

export default App;
