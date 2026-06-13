const trainingAreas = ["防守 1v1", "套边时机", "内收接应", "防反击"];

type StartScreenProps = {
  onStart: () => void;
};

export function StartScreen({ onStart }: StartScreenProps) {
  return (
    <main className="screen start-screen">
      <section className="hero">
        <p className="eyebrow">边后卫决策训练</p>
        <h1>达洛特：上还是不上</h1>
        <p className="subtitle">
          扮演曼联右后卫达洛特，在关键瞬间做出最合理的边路决策。
        </p>
        <button className="primary-button" onClick={onStart}>
          开始训练
        </button>
      </section>

      <section className="training-grid" aria-label="训练方向">
        {trainingAreas.map((area) => (
          <article className="training-card" key={area}>
            <span>{area}</span>
          </article>
        ))}
      </section>
    </main>
  );
}
