import type { Option, Scenario } from "../types/game";

const dimensionLabels = {
  attack: "进攻推进",
  defense: "防守安全",
  space: "空间理解",
  teamwork: "团队协同",
};

type ReviewScreenProps = {
  scenario: Scenario;
  selected: Option;
  onNext: () => void;
  isLast: boolean;
};

export function ReviewScreen({
  scenario,
  selected,
  onNext,
  isLast,
}: ReviewScreenProps) {
  const best = scenario.options.find((option) => option.isBest) ?? selected;

  return (
    <main className="screen review-screen">
      <section className="review-header">
        <p className="eyebrow">复盘</p>
        <h1>{selected.score}</h1>
        <span>本题得分 / 100</span>
      </section>

      <section className="review-grid">
        <article className="review-card">
          <h2>你的选择</h2>
          <p className="choice-label">{selected.label}</p>
        </article>
        <article className="review-card best">
          <h2>最佳选择</h2>
          <p className="choice-label">{best.label}</p>
        </article>
      </section>

      <section className="analysis-panel">
        <h2>战术解释</h2>
        <p>{selected.explanation}</p>
        <h2>教练组复盘</h2>
        <p>{buildDalotReview(scenario, selected, best)}</p>
        <div className="coach-notes">
          <span>扫描重点：{buildScanCue(scenario)}</span>
          <span>触发条件：{buildTriggerCue(scenario, best)}</span>
        </div>
      </section>

      <section className="dimensions-panel">
        {Object.entries(selected.impact).map(([key, value]) => (
          <div className="dimension" key={key}>
            <div className="dimension-label">
              <span>{dimensionLabels[key as keyof typeof dimensionLabels]}</span>
              <strong>{value > 0 ? `+${value}` : value}</strong>
            </div>
            <div className="meter">
              <span style={{ width: `${Math.min(100, value * 3)}%` }} />
            </div>
          </div>
        ))}
      </section>

      <button className="primary-button" onClick={onNext}>
        {isLast ? "查看总结" : "下一题"}
      </button>
    </main>
  );
}

function buildDalotReview(scenario: Scenario, selected: Option, best: Option) {
  if (selected.isBest) {
    return `这次判断很干净。你先读到了“${scenario.mainRisk}”，再根据 B费、右边锋和后腰保护的位置决定行动，像职业边后卫该有的先扫描、再启动。`;
  }

  return `这个选择有一定道理，但你的第一眼没有抓住“${scenario.mainRisk}”。如果换成“${best.label}”，你能更好地平衡推进、身后空间和队友协同。`;
}

function buildScanCue(scenario: Scenario) {
  if (scenario.midfieldCover === "poor" || scenario.spaceBehind === "large") {
    return "先看后腰保护和身后空间，再决定能不能前插。";
  }

  if (scenario.mode === "invert") {
    return "先看中卫出球角度和六号位旁边的接应口。";
  }

  if (scenario.mode === "overlap") {
    return "先看右边锋是否带走左后卫，以及 B费是否有传球角度。";
  }

  return "先看对方边锋强脚方向和协防是否已经到位。";
}

function buildTriggerCue(scenario: Scenario, best: Option) {
  const riskCue =
    scenario.spaceBehind === "large" ? "身后空间大" : `主要风险是${scenario.mainRisk}`;

  return `${riskCue}时，优先考虑“${best.label}”。`;
}
