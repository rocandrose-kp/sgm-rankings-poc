import { useParams, Link, useNavigate } from 'react-router-dom';
import { TournamentResult } from '../types';
import { calculateTeamScores } from '../services/scoringService';

interface ClubDetailPageProps {
  tournaments: TournamentResult[];
}

interface ClubTeam {
  teamId: string;
  teamName: string;
  categoryName: string;
  totalPoints: number;
  tournaments: Array<{
    name: string;
    points: number;
    rank: number;
    stageType: string;
  }>;
}

export const ClubDetailPage = ({ tournaments }: ClubDetailPageProps) => {
  const { clubId } = useParams<{ clubId: string }>();
  const navigate = useNavigate();

  const handleGoBack = () => {
    // Check if there's history to go back to
    if (window.history.state && window.history.state.idx > 0) {
      navigate(-1);
    } else {
      // Fallback to overall clubs page if no history
      navigate('/overall-clubs');
    }
  };

  // Find all teams for this club across all tournaments
  const clubTeamsMap = new Map<string, ClubTeam>();
  let clubName = '';
  let totalClubPoints = 0;

  tournaments.forEach((tournament) => {
    const teamScores = calculateTeamScores(tournament.results);
    
    teamScores.forEach((teamScore) => {
      if (teamScore.clubId === clubId) {
        clubName = teamScore.clubName;
        totalClubPoints += teamScore.totalPoints;

        const key = `${teamScore.teamId}_${teamScore.categoryName}`;
        
        if (clubTeamsMap.has(key)) {
          const existing = clubTeamsMap.get(key)!;
          existing.totalPoints += teamScore.totalPoints;
          
          // Find the rank for this tournament
          const teamResult = tournament.results.find(
            (r) => r.team.teamId === teamScore.teamId
          );
          
          if (teamResult) {
            existing.tournaments.push({
              name: tournament.tournamentName,
              points: teamScore.totalPoints,
              rank: teamResult.rank,
              stageType: teamResult.stageType,
            });
          }
        } else {
          const teamResult = tournament.results.find(
            (r) => r.team.teamId === teamScore.teamId
          );
          
          clubTeamsMap.set(key, {
            teamId: teamScore.teamId,
            teamName: teamScore.teamName,
            categoryName: teamScore.categoryName,
            totalPoints: teamScore.totalPoints,
            tournaments: teamResult ? [{
              name: tournament.tournamentName,
              points: teamScore.totalPoints,
              rank: teamResult.rank,
              stageType: teamResult.stageType,
            }] : [],
          });
        }
      }
    });
  });

  const clubTeams = Array.from(clubTeamsMap.values()).sort((a, b) => {
    if (b.totalPoints !== a.totalPoints) {
      return b.totalPoints - a.totalPoints;
    }
    return a.teamName.localeCompare(b.teamName);
  });

  if (!clubName) {
    return (
      <div className="page-content">
        <div className="page-header">
          <h1>Club Not Found</h1>
          <p>The club you're looking for doesn't exist.</p>
        </div>
        <button onClick={handleGoBack} className="back-button">
          ← Back
        </button>
      </div>
    );
  }

  return (
    <div className="page-content">
      <button onClick={handleGoBack} className="back-button">
        ← Back
      </button>

      <div className="club-detail-header">
        <div className="club-info">
          <h1>{clubName}</h1>
          <p className="club-subtitle">Club Performance Overview</p>
        </div>
        <div className="club-stats">
          <div className="stat-card">
            <span className="stat-label">Total Points</span>
            <span className="stat-value">{totalClubPoints}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Teams</span>
            <span className="stat-value">{clubTeams.length}</span>
          </div>
        </div>
      </div>

      <div className="rankings-card">
        <div className="card-header">
          <h2>Club Teams</h2>
          <span className="result-count">{clubTeams.length} teams</span>
        </div>
        
        {clubTeams.map((team) => (
          <div key={`${team.teamId}_${team.categoryName}`} className="team-card">
            <div className="team-card-header">
              <div>
                <h3 className="team-card-title">
                  <Link to={`/team/${team.teamId}`} className="team-link">
                    {team.teamName}
                  </Link>
                </h3>
                <p className="team-card-category">{team.categoryName}</p>
              </div>
              <div className="team-card-points">
                <span className="points-badge large">{team.totalPoints}</span>
              </div>
            </div>
            
            <div className="team-card-tournaments">
              <h4>Tournament Results:</h4>
              <div className="tournament-results-grid">
                {team.tournaments.map((tournament, idx) => (
                  <div key={idx} className="tournament-result-item">
                    <span className="tournament-result-name">{tournament.name}</span>
                    <div className="tournament-result-details">
                      <span className={`stage-badge ${tournament.stageType.toLowerCase()}`}>
                        {tournament.stageType === 'CUP_FINAL' ? 'Cup' : 'Plate'}
                      </span>
                      <span className="rank-badge-small">
                        {tournament.rank === 1 ? '🥇' : tournament.rank === 2 ? '🥈' : tournament.rank === 3 ? '🥉' : `#${tournament.rank}`}
                      </span>
                      <span className="points-badge-small">{tournament.points} pts</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
