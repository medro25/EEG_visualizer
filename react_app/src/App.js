import React from 'react';
import './App.css';
import EEGVisualizer from './components/EEGVisualizer';

function App() {
  return (
    <div className="App">
      <h1>EEG Data Visualizer</h1>
      <EEGVisualizer />
    </div>
  );
}

export default App;
