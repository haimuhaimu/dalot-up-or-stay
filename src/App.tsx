import { useMemo, useState } from "react";
import { OptionsList } from "./components/OptionsList";
import { ReviewScreen } from "./components/ReviewScreen";
import { ScenarioPanel } from "./components/ScenarioPanel";
import { StartScreen } from "./components/StartScreen";
import { SummaryScreen } from "./components/SummaryScreen";
import { scenarios } from "./data/scenarios";
import type { Dimensions, Option } from "./types/game";

type GameState = "start" | "question" | "review" | "summary";

const emptyDimensions: Dimensions = {
  attack: 0,
  defense: 0,
  space: 0,
  teamwork: 0,
};

export default function App() {
  const [gameState, setGameState] = useState<GameState>("start");
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState<Option | null>(null);
  const [selections, setSelections] = useState<Option[]>([]);

  const currentScenario = scenarios[currentIndex];
  const totals = useMemo(
    () =>
      selections.reduce<Dimensions>(
        (sum, option) => ({
          attack: sum.attack + option.impact.attack,
          defense: sum.defense + option.impact.defense,
          space: sum.space + option.impact.space,
          teamwork: sum.teamwork + option.impact.teamwork,
        }),
        emptyDimensions,
      ),
    [selections],
  );

  function startGame() {
    setGameState("question");
    setCurrentIndex(0);
    setSelectedOption(null);
    setSelections([]);
  }

  function selectOption(option: Option) {
    setSelectedOption(option);
    setSelections((previous) => [...previous, option]);
    setGameState("review");
  }

  function goNext() {
    if (currentIndex === scenarios.length - 1) {
      setGameState("summary");
      return;
    }

    setCurrentIndex((index) => index + 1);
    setSelectedOption(null);
    setGameState("question");
  }

  if (gameState === "start") {
    return <StartScreen onStart={startGame} />;
  }

  if (gameState === "summary") {
    return (
      <SummaryScreen
        selections={selections}
        totals={totals}
        onRestart={startGame}
      />
    );
  }

  if (gameState === "review" && selectedOption) {
    return (
      <ReviewScreen
        scenario={currentScenario}
        selected={selectedOption}
        onNext={goNext}
        isLast={currentIndex === scenarios.length - 1}
      />
    );
  }

  return (
    <main className="screen game-screen">
      <ScenarioPanel
        scenario={currentScenario}
        currentIndex={currentIndex}
        total={scenarios.length}
      />
      <OptionsList options={currentScenario.options} onSelect={selectOption} />
    </main>
  );
}
