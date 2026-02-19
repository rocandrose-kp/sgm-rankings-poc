import React from 'react';
import { Link } from 'react-router-dom';
import { TeamScore } from '../types';

interface TeamRankingsProps {
  teams: TeamScore[];
  limit?: number;
}

export const TeamRankings: React.FC<TeamRankingsProps> = ({ teams, limit = 10 }) => {
  const displayTeams = teams.slice(0, limit);

  return (
    <div className="rankings-section">
      <div className="section-header">
        <h2>🏆 Top Teams</h2>
        <Link to="/scoring" className="scoring-link-header">
          ℹ️ View Scoring System
        </Link>
      </div>
      <div className="rankings-table">
        <table>
          <thead>
            <tr>
              <th className="rank-col">Rank</th>
              <th className="team-col">Team</th>
              <th className="category-col">Category</th>
              <th className="club-col">Club</th>
              <th className="points-col">Points</th>
            </tr>
          </thead>
          <tbody>
            {displayTeams.map((team, index) => (
              <tr key={`${team.teamId}_${team.categoryName}`}>
                <td className="rank-col">
                  <span className={`rank-badge rank-${index + 1}`}>
                    {index + 1}
                  </span>
                </td>
                <td className="team-name">
                  <Link to={`/team/${team.teamId}`} className="team-link">
                    {team.teamName}
                  </Link>
                </td>
                <td className="category-col">{team.categoryName}</td>
                <td className="club-col">{team.clubName}</td>
                <td className="points-col">
                  <span className="points-badge">{team.totalPoints}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
