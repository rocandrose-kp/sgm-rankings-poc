export type StageType = "CUP_FINAL" | "PLATE_FINAL";

export interface Team {
  teamId: string;
  teamName: string;
  clubId: string;
  clubName: string;
}

export interface ResultRow {
  categoryId: string;
  categoryName: string;
  stageType: StageType;
  rank: number;
  team: Team;
}

export interface TournamentResult {
  tournamentId: string;
  tournamentName: string;
  season: string;
  results: ResultRow[];
}

export interface TeamScore {
  teamId: string;
  teamName: string;
  clubId: string;
  clubName: string;
  categoryName: string;
  totalPoints: number;
}

export interface ClubScore {
  clubId: string;
  clubName: string;
  totalPoints: number;
}
