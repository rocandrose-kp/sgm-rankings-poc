import { useState } from 'react';

export const ScoringLegend = () => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="scoring-legend">
      <button 
        className="legend-toggle"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span className="legend-icon">ℹ️</span>
        <span>Scoring System</span>
        <span className={`legend-arrow ${isExpanded ? 'expanded' : ''}`}>▼</span>
      </button>
      
      {isExpanded && (
        <div className="legend-content">
          <div className="legend-section">
            <h4>COPA Division</h4>
            <div className="legend-grid">
              <div className="legend-item">
                <span className="legend-label">Cup Final - 1st:</span>
                <span className="legend-points">24 pts</span>
              </div>
              <div className="legend-item">
                <span className="legend-label">Cup Final - 2nd:</span>
                <span className="legend-points">22 pts</span>
              </div>
              <div className="legend-item">
                <span className="legend-label">Cup Semi-final (3rd/4th):</span>
                <span className="legend-points">20 pts</span>
              </div>
              <div className="legend-item">
                <span className="legend-label">Plate Final - 1st:</span>
                <span className="legend-points">18 pts</span>
              </div>
              <div className="legend-item">
                <span className="legend-label">Plate Final - 2nd:</span>
                <span className="legend-points">16 pts</span>
              </div>
              <div className="legend-item">
                <span className="legend-label">Plate Semi-final (3rd/4th):</span>
                <span className="legend-points">14 pts</span>
              </div>
            </div>
          </div>

          <div className="legend-section">
            <h4>LIGA Division</h4>
            <div className="legend-grid">
              <div className="legend-item">
                <span className="legend-label">Cup Final - 1st:</span>
                <span className="legend-points">12 pts</span>
              </div>
              <div className="legend-item">
                <span className="legend-label">Cup Final - 2nd:</span>
                <span className="legend-points">10 pts</span>
              </div>
              <div className="legend-item">
                <span className="legend-label">Cup Semi-final (3rd/4th):</span>
                <span className="legend-points">8 pts</span>
              </div>
              <div className="legend-item">
                <span className="legend-label">Plate Final - 1st:</span>
                <span className="legend-points">6 pts</span>
              </div>
              <div className="legend-item">
                <span className="legend-label">Plate Final - 2nd:</span>
                <span className="legend-points">4 pts</span>
              </div>
              <div className="legend-item">
                <span className="legend-label">Plate Semi-final (3rd/4th):</span>
                <span className="legend-points">2 pts</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
