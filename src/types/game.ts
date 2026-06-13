export type ScenarioMode = "defense" | "overlap" | "invert" | "transition";

export type CoverLevel = "good" | "average" | "poor";

export type SpaceLevel = "small" | "medium" | "large";

export type Option = {
  id: string;
  label: string;
  score: number;
  isBest: boolean;
  explanation: string;
  impact: {
    attack: number;
    defense: number;
    space: number;
    teamwork: number;
  };
};

export type Scenario = {
  id: number;
  mode: ScenarioMode;
  minute: string;
  score: string;
  opponent: string;
  formation: string;
  ballPosition: string;
  brunoPosition: string;
  rightWingerPosition: string;
  midfieldCover: CoverLevel;
  opponentWinger: string;
  spaceBehind: SpaceLevel;
  mainRisk: string;
  description: string;
  question: string;
  options: Option[];
};

export type Dimensions = {
  attack: number;
  defense: number;
  space: number;
  teamwork: number;
};
