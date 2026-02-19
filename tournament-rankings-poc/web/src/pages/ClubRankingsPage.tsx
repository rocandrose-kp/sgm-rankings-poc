import { ClubScore } from '../types';
import { ClubRankings } from '../components/ClubRankings';

interface ClubRankingsPageProps {
  clubScores: ClubScore[];
  tournamentName: string;
  totalResults: number;
}

export const ClubRankingsPage = ({ clubScores, tournamentName, totalResults }: ClubRankingsPageProps) => {
  return (
    <div className="page-content">
      <div className="page-header">
        <h1>Club Rankings</h1>
        <p>{tournamentName} - {totalResults} Results</p>
      </div>
      <ClubRankings clubs={clubScores} limit={50} />
    </div>
  );
};
