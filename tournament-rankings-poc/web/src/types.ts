export type StageType = "CUP_FINAL" | "PLATE_FINAL";
export type Division = "COPA" | "LIGA" | "OTHER";

export interface Team {
  teamId: string;
  teamName: string;
  clubId: string;
  clubName: string;
}

export interface MatchScore {
  opponent: string;
  opponentId: string;
  homeGoals: number;
  awayGoals: number;
  isHome: boolean;
  result: 'won' | 'lost';
  roundName: string;
  penalties: boolean;
}

export interface ResultRow {
  categoryId: string;
  categoryName: string;
  stageType: StageType;
  rank: number;
  team: Team;
  matches?: MatchScore[];
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
