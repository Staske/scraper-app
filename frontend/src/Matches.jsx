import React, { useState, useEffect } from "react";
import './matches.css';

function Matches() {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMatches = async () => {
      try {
        const response = await fetch('http://localhost:5000/matches');
        const data = await response.json();
        setMatches(data);
      } catch (error) {
        console.error("Error fetching matches:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchMatches();
  }, []);

  return (
    <div className="match-container">
      <h1>Euroleague Basketball Matches</h1>

      {loading ? (
        <p className="loading">Loading matches...</p>
      ) : (
        matches.map((match, index) => (
          <div className="match-card" key={index}>
            <div className="home-team">
              <div className="team-name">{match.home_team}</div>
            </div>
            <div className="score">
              {match.score_home} - {match.score_away}
            </div>
            <div className="away-team">
              <div className="team-name">{match.away_team}</div>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

export default Matches;
