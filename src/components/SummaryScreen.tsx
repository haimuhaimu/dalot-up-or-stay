import type { Dimensions, Option } from "../types/game";

type SummaryScreenProps = {
  selections: Option[];
  totals: Dimensions;
  onRestart: () => void;
};

export function SummaryScreen({
  selections,
  totals,
  onRestart,
}: SummaryScreenProps) {
  const totalScore = selections.reduce((sum, option) => sum + option.score, 0);
  const averageScore = Math.round(totalScore / selections.length);
  const profile = getProfile(selections, totals);
  const issues = getIssues(selections, totals);
  const advice = getAdvice(profile.title);

  return (
    <main className="screen summary-screen">
      <section className="summary-hero">
        <p className="eyebrow">训练完成</p>
        <h1>{totalScore}</h1>
        <p>总分</p>
        <div className="average-score">平均分：{averageScore}</div>
      </section>

      <section className="summary-section">
        <h2>玩家边后卫风格画像</h2>
        <article className="profile-card">
          <strong>{profile.title}</strong>
          <p>{profile.description}</p>
        </article>
      </section>

      <section className="summary-section">
        <h2>四维表现</h2>
        <div className="dimension-summary">
          <span>进攻推进 {totals.attack}</span>
          <span>防守安全 {totals.defense}</span>
          <span>空间理解 {totals.space}</span>
          <span>团队协同 {totals.teamwork}</span>
        </div>
      </section>

      <section className="summary-section">
        <h2>常见问题</h2>
        <ul className="plain-list">
          {issues.map((issue) => (
            <li key={issue}>{issue}</li>
          ))}
        </ul>
      </section>

      <section className="summary-section">
        <h2>下一轮训练建议</h2>
        <p>{advice}</p>
      </section>

      <button className="primary-button" onClick={onRestart}>
        再来一轮
      </button>
    </main>
  );
}

function getProfile(selections: Option[], totals: Dimensions) {
  const average = selections.reduce((sum, option) => sum + option.score, 0) / selections.length;

  if (totals.attack > totals.defense + 35) {
    return {
      title: "莽夫型达洛特",
      description: "喜欢前插和上抢，冲击力强，但有时会把身后空间留给对手。",
    };
  }

  if (totals.defense > totals.attack + 45) {
    return {
      title: "稳健型达洛特",
      description: "防守选择保守，安全性高，但进攻参与和第三人跑动还可以更主动。",
    };
  }

  if (totals.space >= totals.attack && totals.space >= totals.defense) {
    return {
      title: "内收大师",
      description: "擅长保护中路和帮助出球，能读懂队友站位之间的隐藏线路。",
    };
  }

  if (average >= 86 && totals.attack >= totals.defense - 10) {
    return {
      title: "右路发动机",
      description: "进攻参与积极，套边时机好，也知道什么时候该把球权交给队友提速。",
    };
  }

  return {
    title: "防反击专家",
    description: "能识别危险，优先保护身后空间，在领先和转换阶段很可靠。",
  };
}

function getIssues(selections: Option[], totals: Dimensions) {
  const lowScores = selections.filter((option) => option.score < 70).length;
  const issues: string[] = [];

  if (lowScores >= 3) {
    issues.push("低分选择偏多，说明你在局面触发点上还需要更快识别主风险。");
  }

  if (totals.attack < 150) {
    issues.push("进攻推进偏少，面对低位防守时可以更主动提供第三人接应。");
  }

  if (totals.defense < 190) {
    issues.push("防守安全值偏低，前插前要先确认后腰保护和身后空间。");
  }

  if (totals.teamwork < 190) {
    issues.push("团队协同还有提升空间，边后卫决策经常取决于 B费和右边锋的位置。");
  }

  return issues.length ? issues : ["整体选择均衡，没有明显短板，下一步可以提高决策速度。"];
}

function getAdvice(profile: string) {
  const adviceMap: Record<string, string> = {
    莽夫型达洛特: "重点训练防反击识别：每次前插前先问自己，后腰保护是否到位，身后空间是否可控。",
    稳健型达洛特: "重点训练套边时机：当右边锋内收、B费抬头、后腰保护到位时，要敢于提供纵深。",
    内收大师: "继续强化中路接应，同时练习从内收到外插的二次启动，让对手更难判断你的路线。",
    右路发动机: "下一轮可以提高难度，专门训练比赛末段的风险收益判断。",
    防反击专家: "保持防守预判优势，再补一些低位进攻里的倒三角和延迟套边选择。",
  };

  return adviceMap[profile];
}
