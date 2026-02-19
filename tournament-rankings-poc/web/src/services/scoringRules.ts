import { StageType, Division } from "../types";

export interface ScoringRule {
  division: Division;
  stageType: StageType;
  rank: number;
  points: number;
}

export const scoringRules: ScoringRule[] = [
  // COPA Cup Finals
  { division: "COPA", stageType: "CUP_FINAL", rank: 1, points: 24 },
  { division: "COPA", stageType: "CUP_FINAL", rank: 2, points: 22 },
  { division: "COPA", stageType: "CUP_FINAL", rank: 3, points: 20 },
  { division: "COPA", stageType: "CUP_FINAL", rank: 4, points: 20 },
  
  // COPA Plate Finals
  { division: "COPA", stageType: "PLATE_FINAL", rank: 1, points: 18 },
  { division: "COPA", stageType: "PLATE_FINAL", rank: 2, points: 16 },
  { division: "COPA", stageType: "PLATE_FINAL", rank: 3, points: 14 },
  { division: "COPA", stageType: "PLATE_FINAL", rank: 4, points: 14 },
  
  // LIGA Cup Finals
  { division: "LIGA", stageType: "CUP_FINAL", rank: 1, points: 12 },
  { division: "LIGA", stageType: "CUP_FINAL", rank: 2, points: 10 },
  { division: "LIGA", stageType: "CUP_FINAL", rank: 3, points: 8 },
  { division: "LIGA", stageType: "CUP_FINAL", rank: 4, points: 8 },
  
  // LIGA Plate Finals
  { division: "LIGA", stageType: "PLATE_FINAL", rank: 1, points: 6 },
  { division: "LIGA", stageType: "PLATE_FINAL", rank: 2, points: 4 },
  { division: "LIGA", stageType: "PLATE_FINAL", rank: 3, points: 2 },
  { division: "LIGA", stageType: "PLATE_FINAL", rank: 4, points: 2 },
  
  // Default for OTHER divisions (use LIGA scoring)
  { division: "OTHER", stageType: "CUP_FINAL", rank: 1, points: 12 },
  { division: "OTHER", stageType: "CUP_FINAL", rank: 2, points: 10 },
  { division: "OTHER", stageType: "CUP_FINAL", rank: 3, points: 8 },
  { division: "OTHER", stageType: "CUP_FINAL", rank: 4, points: 8 },
  { division: "OTHER", stageType: "PLATE_FINAL", rank: 1, points: 6 },
  { division: "OTHER", stageType: "PLATE_FINAL", rank: 2, points: 4 },
  { division: "OTHER", stageType: "PLATE_FINAL", rank: 3, points: 2 },
  { division: "OTHER", stageType: "PLATE_FINAL", rank: 4, points: 2 },
];
