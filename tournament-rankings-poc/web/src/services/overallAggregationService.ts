import { TournamentResult, TeamScore, ClubScore } from '../types';
import { calculateTeamScores } from './scoringService';
import { aggregateClubScores } from './aggregationService';

export interface OverallTeamScore extends TeamScore {
  tournaments: string[];
}

export interface OverallClubScore extends ClubScore {
  tournaments: string[];
}

export function calculateOverallTeamScores(tournaments: TournamentResult[]): OverallTeamScore[] {
  const teamScoresMap = new Map<string, OverallTeamScore>();

  tournaments.forEach((tournament) => {
    const teamScores = calculateTeamScores(tournament.results);
    
    teamScores.forEach((score) => {
      const key = `${score.teamId}`;
      
      if (teamScoresMap.has(key)) {
        const existing = teamScoresMap.get(key)!;
        existing.totalPoints += score.totalPoints;
        if (!existing.tournaments.includes(tournament.tournamentName)) {
          existing.tournaments.push(tournament.tournamentName);
        }
      } else {
        teamScoresMap.set(key, {
          ...score,
          tournaments: [tournament.tournamentName],
        });
      }
    });
  });

  const overallScores = Array.from(teamScoresMap.values());
  return overallScores.sort((a, b) => {
    if (b.totalPoints !== a.totalPoints) {
      return b.totalPoints - a.totalPoints;
    }
    return a.teamName.localeCompare(b.teamName);
  });
}

export function calculateOverallClubScores(tournaments: TournamentResult[]): OverallClubScore[] {
  const clubScoresMap = new Map<string, OverallClubScore>();

  tournaments.forEach((tournament) => {
    const teamScores = calculateTeamScores(tournament.results);
    const clubScores = aggregateClubScores(teamScores);
    
    clubScores.forEach((score) => {
      const key = score.clubId;
      
      if (clubScoresMap.has(key)) {
        const existing = clubScoresMap.get(key)!;
        existing.totalPoints += score.totalPoints;
        if (!existing.tournaments.includes(tournament.tournamentName)) {
          existing.tournaments.push(tournament.tournamentName);
        }
      } else {
        clubScoresMap.set(key, {
          ...score,
          tournaments: [tournament.tournamentName],
        });
      }
    });
  });

  const overallScores = Array.from(clubScoresMap.values());
  return overallScores.sort((a, b) => {
    if (b.totalPoints !== a.totalPoints) {
      return b.totalPoints - a.totalPoints;
    }
    return a.clubName.localeCompare(b.clubName);
  });
}
