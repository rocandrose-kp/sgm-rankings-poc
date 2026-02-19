import React from 'react';
import { Link } from 'react-router-dom';
import { ClubScore } from '../types';

interface ClubRankingsProps {
  clubs: ClubScore[];
  limit?: number;
}

export const ClubRankings: React.FC<ClubRankingsProps> = ({ clubs, limit = 10 }) => {
  const displayClubs = clubs.slice(0, limit);

  return (
    <div className="rankings-section">
      <div className="section-header">
        <h2>🏅 Top Clubs</h2>
        <Link to="/scoring" className="scoring-link-header">
          ℹ️ View Scoring System
        </Link>
      </div>
      <div className="rankings-table">
        <table>
          <thead>
            <tr>
              <th className="rank-col">Rank</th>
              <th className="club-col">Club</th>
              <th className="points-col">Total Points</th>
            </tr>
          </thead>
          <tbody>
            {displayClubs.map((club, index) => (
              <tr key={club.clubId}>
                <td className="rank-col">
                  <span className={`rank-badge rank-${index + 1}`}>
                    {index + 1}
                  </span>
                </td>
                <td className="club-name">
                  <Link to={`/club/${club.clubId}`} className="team-link">
                    {club.clubName}
                  </Link>
                </td>
                <td className="points-col">
                  <span className="points-badge">{club.totalPoints}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
