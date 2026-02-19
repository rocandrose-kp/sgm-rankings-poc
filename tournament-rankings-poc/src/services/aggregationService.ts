import { TeamScore, ClubScore } from "../models/domain";

export function aggregateClubScores(teamScores: TeamScore[]): ClubScore[] {
  const clubScoresMap = new Map<string, ClubScore>();

  for (const teamScore of teamScores) {
    if (clubScoresMap.has(teamScore.clubId)) {
      const existing = clubScoresMap.get(teamScore.clubId)!;
      existing.totalPoints += teamScore.totalPoints;
    } else {
      clubScoresMap.set(teamScore.clubId, {
        clubId: teamScore.clubId,
        clubName: teamScore.clubName,
        totalPoints: teamScore.totalPoints,
      });
    }
  }

  const clubScores = Array.from(clubScoresMap.values());
  return sortClubScores(clubScores);
}

export function sortClubScores(clubScores: ClubScore[]): ClubScore[] {
  return clubScores.sort((a, b) => {
    if (b.totalPoints !== a.totalPoints) {
      return b.totalPoints - a.totalPoints;
    }
    return a.clubName.localeCompare(b.clubName);
  });
}
