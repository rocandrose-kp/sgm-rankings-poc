import React from 'react';

interface TournamentHeaderProps {
  tournamentName: string;
  season: string;
  tournamentId: string;
  totalResults: number;
}

export const TournamentHeader: React.FC<TournamentHeaderProps> = ({
  tournamentName,
  season,
  tournamentId,
  totalResults,
}) => {
  return (
    <div className="tournament-header">
      <h1>{tournamentName} {season}</h1>
      <div className="tournament-meta">
        <span>Tournament ID: {tournamentId}</span>
        <span>•</span>
        <span>Season: {season}</span>
        <span>•</span>
        <span>{totalResults} Results</span>
      </div>
    </div>
  );
};
