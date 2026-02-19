import { TeamScore } from '../types';
import { TeamRankings } from '../components/TeamRankings';

interface TeamRankingsPageProps {
  teamScores: TeamScore[];
  tournamentName: string;
  totalResults: number;
}

export const TeamRankingsPage = ({ teamScores, tournamentName, totalResults }: TeamRankingsPageProps) => {
  return (
    <div className="page-content">
      <div className="page-header">
        <h1>Team Rankings</h1>
        <p>{tournamentName} - {totalResults} Results</p>
      </div>
      <TeamRankings teams={teamScores} limit={50} />
    </div>
  );
};
