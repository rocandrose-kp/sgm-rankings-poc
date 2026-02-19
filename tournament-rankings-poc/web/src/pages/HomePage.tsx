export const HomePage = () => {
  return (
    <div className="home-page">
      <div className="hero-section">
        <h1>Welcome to Tournament Rankings</h1>
        <p>Track team and club performance across tournaments</p>
      </div>

      <div className="quick-links">
        <h3>Explore Rankings</h3>
        <div className="link-grid">
          <a href="/tournaments" className="link-card">
            <span className="link-icon">🏟️</span>
            <h4>Tournaments</h4>
            <p>View individual tournament rankings by age, gender, and division</p>
          </a>
          <a href="/overall-teams" className="link-card">
            <span className="link-icon">🏆</span>
            <h4>Overall Teams</h4>
            <p>Combined team rankings across all tournaments</p>
          </a>
          <a href="/overall-clubs" className="link-card">
            <span className="link-icon">🏅</span>
            <h4>Overall Clubs</h4>
            <p>Combined club rankings across all tournaments</p>
          </a>
        </div>
      </div>
    </div>
  );
};
