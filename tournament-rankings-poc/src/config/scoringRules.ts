import { StageType } from "../models/domain";

export interface ScoringRule {
  stageType: StageType;
  rank: number;
  points: number;
}

export const scoringRules: ScoringRule[] = [
  { stageType: "CUP_FINAL", rank: 1, points: 12 },
  { stageType: "CUP_FINAL", rank: 2, points: 10 },
  { stageType: "CUP_FINAL", rank: 3, points: 8 },
  { stageType: "CUP_FINAL", rank: 4, points: 6 },
  { stageType: "PLATE_FINAL", rank: 1, points: 6 },
  { stageType: "PLATE_FINAL", rank: 2, points: 4 },
  { stageType: "PLATE_FINAL", rank: 3, points: 2 },
  { stageType: "PLATE_FINAL", rank: 4, points: 1 },
];
