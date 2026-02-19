import { ResultRow, TeamScore, StageType, Division } from "../types";
import { scoringRules } from "./scoringRules";
import { extractDivisionFromCategory } from "../utils/categoryParser";

export function getPoints(stageType: StageType, rank: number, categoryName: string): number {
  const divisionStr = extractDivisionFromCategory(categoryName);
  const division: Division = divisionStr === "COPA" ? "COPA" : divisionStr === "LIGA" ? "LIGA" : "OTHER";
  
  const rule = scoringRules.find(
    (r) => r.division === division && r.stageType === stageType && r.rank === rank
  );
  return rule ? rule.points : 0;
}

export function calculateTeamScores(results: ResultRow[]): TeamScore[] {
  const teamScoresMap = new Map<string, TeamScore>();

  for (const result of results) {
    if (!result.stageType || !result.rank) {
      console.warn(
        `Skipping result with missing data: ${JSON.stringify(result)}`
      );
      continue;
    }

    const points = getPoints(result.stageType, result.rank, result.categoryName);
    const key = `${result.team.teamId}_${result.categoryId}`;

    if (teamScoresMap.has(key)) {
      const existing = teamScoresMap.get(key)!;
      existing.totalPoints += points;
    } else {
      teamScoresMap.set(key, {
        teamId: result.team.teamId,
        teamName: result.team.teamName,
        clubId: result.team.clubId,
        clubName: result.team.clubName,
        categoryName: result.categoryName,
        totalPoints: points,
      });
    }
  }

  const teamScores = Array.from(teamScoresMap.values());
  return sortTeamScores(teamScores);
}

export function sortTeamScores(teamScores: TeamScore[]): TeamScore[] {
  return teamScores.sort((a, b) => {
    if (b.totalPoints !== a.totalPoints) {
      return b.totalPoints - a.totalPoints;
    }
    return a.teamName.localeCompare(b.teamName);
  });
}
