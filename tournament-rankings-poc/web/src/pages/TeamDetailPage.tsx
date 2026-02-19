import { useParams, useNavigate } from 'react-router-dom';
import { TournamentResult, MatchScore } from '../types';
import { calculateTeamScores } from '../services/scoringService';

interface TeamDetailPageProps {
  tournaments: TournamentResult[];
}

export const TeamDetailPage = ({ tournaments }: TeamDetailPageProps) => {
  const { teamId } = useParams<{ teamId: string }>();
  const navigate = useNavigate();

  const handleGoBack = () => {
    // Check if there's history to go back to
    if (window.history.state && window.history.state.idx > 0) {
      navigate(-1);
    } else {
      // Fallback to overall teams page if no history
      navigate('/overall-teams');
    }
  };

  // Find all results for this team across all tournaments
  const teamResults: Array<{
    tournament: string;
    categoryName: string;
    stageType: string;
    rank: number;
    points: number;
    matches?: MatchScore[];
  }> = [];

  let teamName = '';
  let clubName = '';
  let totalPoints = 0;

  tournaments.forEach((tournament) => {
    const teamScores = calculateTeamScores(tournament.results);
    const teamScore = teamScores.find((score) => score.teamId === teamId);

    if (teamScore) {
      teamName = teamScore.teamName;
      clubName = teamScore.clubName;
      totalPoints += teamScore.totalPoints;

      // Find the specific results for this team in this tournament
      const results = tournament.results.filter(
        (result) => result.team.teamId === teamId
      );

      results.forEach((result) => {
        teamResults.push({
          tournament: tournament.tournamentName,
          categoryName: result.categoryName,
          stageType: result.stageType,
          rank: result.rank,
          points: teamScore.totalPoints,
          matches: result.matches,
        });
      });
    }
  });

  if (!teamName) {
    return (
      <div className="page-content">
        <div className="page-header">
          <h1>Team Not Found</h1>
          <p>The team you're looking for doesn't exist.</p>
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

      <div className="team-detail-header">
        <div className="team-info">
          <h1>{teamName}</h1>
          <p className="club-name">{clubName}</p>
        </div>
        <div className="team-stats">
          <div className="stat-card">
            <span className="stat-label">Total Points</span>
            <span className="stat-value">{totalPoints}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Tournaments</span>
            <span className="stat-value">{teamResults.length}</span>
          </div>
        </div>
      </div>

      <div className="rankings-card">
        <div className="card-header">
          <h2>Tournament Results</h2>
        </div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Tournament</th>
                <th>Category</th>
                <th>Stage</th>
                <th>Rank</th>
                <th>Points</th>
              </tr>
            </thead>
            <tbody>
              {teamResults.map((result, index) => (
                <tr key={index}>
                  <td className="tournament-name">{result.tournament}</td>
                  <td>{result.categoryName}</td>
                  <td>
                    <span className={`stage-badge ${result.stageType.toLowerCase()}`}>
                      {result.stageType === 'CUP_FINAL' ? 'Cup Final' : 'Plate Final'}
                    </span>
                  </td>
                  <td>
                    <span className={`rank-badge rank-${result.rank}`}>
                      {result.rank === 1 ? '🥇' : result.rank === 2 ? '🥈' : result.rank === 3 ? '🥉' : result.rank}
                    </span>
                  </td>
                  <td>
                    <span className="points-badge">{result.points}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {teamResults.some(r => r.matches && r.matches.length > 0) && (
        <div className="rankings-card">
          <div className="card-header">
            <h2>Match Results</h2>
          </div>
          <div className="matches-container">
            {teamResults.map((result, resultIndex) => (
              result.matches && result.matches.length > 0 && (
                <div key={resultIndex} className="match-group">
                  <h3 className="match-group-title">{result.tournament} - {result.categoryName}</h3>
                  {result.matches.map((match, matchIndex) => {
                    const teamGoals = match.isHome ? match.homeGoals : match.awayGoals;
                    const oppGoals = match.isHome ? match.awayGoals : match.homeGoals;
                    const resultText = match.result === 'won' ? 'Won' : 'Lost';
                    const resultClass = match.result === 'won' ? 'match-won' : 'match-lost';
                    
                    return (
                      <div key={matchIndex} className={`match-card ${resultClass}`}>
                        <div className="match-result">
                          <span className="match-result-text">{resultText}</span>
                          <span className="match-score">{teamGoals}-{oppGoals}</span>
                        </div>
                        <div className="match-details">
                          <span className="match-opponent">vs {match.opponent}</span>
                          <span className="match-round">{match.roundName}</span>
                          {match.penalties && <span className="match-penalties">⚽ Penalties</span>}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
