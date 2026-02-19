import { Link, useNavigate } from 'react-router-dom';
import { OverallClubScore } from '../services/overallAggregationService';

interface OverallClubRankingsPageProps {
  clubScores: OverallClubScore[];
}

export const OverallClubRankingsPage = ({ clubScores }: OverallClubRankingsPageProps) => {
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
        <h1>Overall Club Rankings</h1>
        <p>Combined scores across all tournaments</p>
      </div>

      <div className="rankings-card">
        <div className="card-header">
          <h2>🏅 Top Clubs (All Tournaments)</h2>
          <div className="header-actions">
            <Link to="/scoring" className="scoring-link-header">
              ℹ️ View Scoring System
            </Link>
            <span className="result-count">{clubScores.length} clubs</span>
          </div>
        </div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Club</th>
                <th>Tournaments</th>
                <th>Total Points</th>
              </tr>
            </thead>
            <tbody>
              {clubScores.map((club, index) => (
                <tr key={club.clubId}>
                  <td>
                    <span className={`rank-badge rank-${index + 1}`}>
                      {index + 1}
                    </span>
                  </td>
                  <td className="club-name">
                    <Link to={`/club/${club.clubId}`} className="team-link">
                      {club.clubName}
                    </Link>
                  </td>
                  <td className="tournaments-col">
                    <div className="tournament-list">
                      {club.tournaments.map((tournament, idx) => (
                        <span key={idx} className="tournament-tag">
                          {tournament}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td>
                    <span className="points-badge">{club.totalPoints}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
