import { useNavigate } from 'react-router-dom';

export const ScoringPage = () => {
  const navigate = useNavigate();

  const handleGoBack = () => {
    // Check if there's history to go back to
    if (window.history.state && window.history.state.idx > 0) {
      navigate(-1);
    } else {
      // Fallback to home page if no history
      navigate('/');
    }
  };

  return (
    <div className="page-content">
      <button onClick={handleGoBack} className="back-button">
        ← Back
      </button>

      <div className="page-header">
        <h1>Scoring System</h1>
        <p>How points are awarded for tournament placements</p>
      </div>

      <div className="scoring-explanation">
        <p>
          Teams earn points based on their final placement in each tournament category. 
          Points vary by division (COPA vs LIGA) and stage type (Cup Finals vs Plate Finals). 
          Semi-final placements (3rd and 4th place) also earn points.
        </p>
      </div>

      <div className="scoring-sections">
        <div className="scoring-division-card">
          <div className="scoring-division-header copa">
            <h2>COPA Division</h2>
            <p>Higher-tier competitive division</p>
          </div>
          
          <div className="scoring-stage-section">
            <h3>Cup Finals</h3>
            <div className="scoring-items">
              <div className="scoring-item">
                <div className="placement-info">
                  <span className="placement-medal">🥇</span>
                  <span className="placement-text">1st Place</span>
                </div>
                <span className="scoring-points-large">24 points</span>
              </div>
              <div className="scoring-item">
                <div className="placement-info">
                  <span className="placement-medal">🥈</span>
                  <span className="placement-text">2nd Place</span>
                </div>
                <span className="scoring-points-large">22 points</span>
              </div>
              <div className="scoring-item">
                <div className="placement-info">
                  <span className="placement-medal">🥉</span>
                  <span className="placement-text">Semi-finals (3rd/4th)</span>
                </div>
                <span className="scoring-points-large">20 points</span>
              </div>
            </div>
          </div>

          <div className="scoring-stage-section">
            <h3>Plate Finals</h3>
            <div className="scoring-items">
              <div className="scoring-item">
                <div className="placement-info">
                  <span className="placement-medal">🥇</span>
                  <span className="placement-text">1st Place</span>
                </div>
                <span className="scoring-points-large">18 points</span>
              </div>
              <div className="scoring-item">
                <div className="placement-info">
                  <span className="placement-medal">🥈</span>
                  <span className="placement-text">2nd Place</span>
                </div>
                <span className="scoring-points-large">16 points</span>
              </div>
              <div className="scoring-item">
                <div className="placement-info">
                  <span className="placement-medal">🥉</span>
                  <span className="placement-text">Semi-finals (3rd/4th)</span>
                </div>
                <span className="scoring-points-large">14 points</span>
              </div>
            </div>
          </div>
        </div>

        <div className="scoring-division-card">
          <div className="scoring-division-header liga">
            <h2>LIGA Division</h2>
            <p>Development-focused division</p>
          </div>
          
          <div className="scoring-stage-section">
            <h3>Cup Finals</h3>
            <div className="scoring-items">
              <div className="scoring-item">
                <div className="placement-info">
                  <span className="placement-medal">🥇</span>
                  <span className="placement-text">1st Place</span>
                </div>
                <span className="scoring-points-large">12 points</span>
              </div>
              <div className="scoring-item">
                <div className="placement-info">
                  <span className="placement-medal">🥈</span>
                  <span className="placement-text">2nd Place</span>
                </div>
                <span className="scoring-points-large">10 points</span>
              </div>
              <div className="scoring-item">
                <div className="placement-info">
                  <span className="placement-medal">🥉</span>
                  <span className="placement-text">Semi-finals (3rd/4th)</span>
                </div>
                <span className="scoring-points-large">8 points</span>
              </div>
            </div>
          </div>

          <div className="scoring-stage-section">
            <h3>Plate Finals</h3>
            <div className="scoring-items">
              <div className="scoring-item">
                <div className="placement-info">
                  <span className="placement-medal">🥇</span>
                  <span className="placement-text">1st Place</span>
                </div>
                <span className="scoring-points-large">6 points</span>
              </div>
              <div className="scoring-item">
                <div className="placement-info">
                  <span className="placement-medal">🥈</span>
                  <span className="placement-text">2nd Place</span>
                </div>
                <span className="scoring-points-large">4 points</span>
              </div>
              <div className="scoring-item">
                <div className="placement-info">
                  <span className="placement-medal">🥉</span>
                  <span className="placement-text">Semi-finals (3rd/4th)</span>
                </div>
                <span className="scoring-points-large">2 points</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="scoring-note">
        <h3>Note</h3>
        <p>
          Club rankings are calculated by summing all points earned by teams from that club 
          across all age groups, genders, and divisions within a tournament. Overall rankings 
          combine points from all tournaments in the season.
        </p>
      </div>
    </div>
  );
};
