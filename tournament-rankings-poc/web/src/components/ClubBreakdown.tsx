import React from 'react';
import { ClubScore, TeamScore } from '../types';

interface ClubBreakdownProps {
  clubs: ClubScore[];
  teams: TeamScore[];
}

export const ClubBreakdown: React.FC<ClubBreakdownProps> = ({ clubs, teams }) => {
  return (
    <div className="breakdown-section">
      <h2>📊 Detailed Club Breakdown</h2>
      <div className="club-breakdown">
        {clubs.map((club) => {
          const clubTeams = teams.filter((t) => t.clubId === club.clubId);
          return (
            <div key={club.clubId} className="club-card">
              <div className="club-card-header">
                <h3>{club.clubName}</h3>
                <span className="club-total">{club.totalPoints} pts</span>
              </div>
              <div className="club-card-body">
                {clubTeams.map((team) => (
                  <div key={`${team.teamId}_${team.categoryName}`} className="team-row">
                    <span className="team-name">{team.teamName}</span>
                    <span className="team-points">{team.totalPoints} pts</span>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
