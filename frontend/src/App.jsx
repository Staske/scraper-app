import React, { useState } from 'react';
import Matches from './components/Matches';
import ESPNNews from './components/ESPNNews';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState("matches");

  return (
    <div className="App">

            
      <nav className="menu">
        <button
          className={activeTab === "matches" ? "active" : ""}
          onClick={() => setActiveTab("matches")}
        >
          Matches
        </button>
        <button
          className={activeTab === "espn" ? "active" : ""}
          onClick={() => setActiveTab("espn")}
        >
          ESPN News
        </button>
      </nav>

      <div style={{ paddingTop: "70px" }}>
        {activeTab === "matches" ? <Matches /> : <ESPNNews />}
      </div>
      {/* Add padding-top to avoid content being hidden under the fixed nav */}
    </div>
  );
}

export default App;
