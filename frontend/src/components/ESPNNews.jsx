import React, { useState, useEffect } from "react";
import "./espnNews.css";

function ESPNNews() {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/espn');
        const data = await response.json();
        setNews(data);
      } catch (error) {
        console.error("Error fetching ESPN news:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchNews();
  }, []);

  return (
    <div className="espn-news-container">
      <h1>ESPN News</h1>
      {loading ? (
        <p className="loading">Loading ESPN news...</p>
      ) : (
        news.map((post, index) => (
          <div className="news-card" key={index}>
            <div className="news-header">
              <h2>{post.contributor}</h2>
              <p className="date">{post.full_date}</p>
            </div>
            <div className="news-body">
              <p>{post.text}</p>
            </div>
            <div className="news-footer">
              <a href={post.url} target="_blank" rel="noopener noreferrer">
                Read more
              </a>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

export default ESPNNews;
