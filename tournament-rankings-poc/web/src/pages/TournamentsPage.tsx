import { Link } from 'react-router-dom';
import { TournamentResult } from '../types';
import { calculateTeamScores } from '../services/scoringService';
import { aggregateClubScores } from '../services/aggregationService';

interface TournamentsPageProps {
  tournaments: TournamentResult[];
}

export const TournamentsPage = ({ tournaments }: TournamentsPageProps) => {
  return (
    <div className="page-content">
      <div className="page-header">
        <h1>Tournaments</h1>
        <p>View details for each tournament</p>
      </div>

      <div className="tournaments-grid">
        {tournaments.map((tournament) => {
          const teamScores = calculateTeamScores(tournament.results);
          const clubScores = aggregateClubScores(teamScores);
          
          // Get unique categories
          const categories = new Set(tournament.results.map(r => r.categoryName));
          
          return (
            <Link 
              key={tournament.tournamentId} 
              to={`/tournament/${tournament.tournamentId}`}
              className="tournament-card-link"
            >
              <div className="tournament-card">
                <div className="tournament-card-header">
                  <h2>{tournament.tournamentName}</h2>
                  <span className="tournament-season">{tournament.season}</span>
                </div>
                <div className="tournament-card-stats">
                  <div className="tournament-stat">
                    <span className="stat-icon">🏆</span>
                    <div>
                      <span className="stat-number">{teamScores.length}</span>
                      <span className="stat-label">Teams</span>
                    </div>
                  </div>
                  <div className="tournament-stat">
                    <span className="stat-icon">🏅</span>
                    <div>
                      <span className="stat-number">{clubScores.length}</span>
                      <span className="stat-label">Clubs</span>
                    </div>
                  </div>
                  <div className="tournament-stat">
                    <span className="stat-icon">📊</span>
                    <div>
                      <span className="stat-number">{categories.size}</span>
                      <span className="stat-label">Categories</span>
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
};
