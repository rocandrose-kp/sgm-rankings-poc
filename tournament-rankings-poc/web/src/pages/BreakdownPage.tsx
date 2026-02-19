import { ClubScore, TeamScore } from '../types';
import { ClubBreakdown } from '../components/ClubBreakdown';

interface BreakdownPageProps {
  clubScores: ClubScore[];
  teamScores: TeamScore[];
  tournamentName: string;
  totalResults: number;
}

export const BreakdownPage = ({ clubScores, teamScores, tournamentName, totalResults }: BreakdownPageProps) => {
  return (
    <div className="page-content">
      <div className="page-header">
        <h1>Club Breakdown</h1>
        <p>{tournamentName} - {totalResults} Results</p>
      </div>
      <ClubBreakdown clubs={clubScores} teams={teamScores} />
    </div>
  );
};
