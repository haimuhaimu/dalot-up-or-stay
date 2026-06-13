import type { Scenario } from "../types/game";

const coverLabels = {
  good: "良好",
  average: "一般",
  poor: "不足",
};

const spaceLabels = {
  small: "小",
  medium: "中",
  large: "大",
};

type ScenarioPanelProps = {
  scenario: Scenario;
  currentIndex: number;
  total: number;
};

export function ScenarioPanel({
  scenario,
  currentIndex,
  total,
}: ScenarioPanelProps) {
  const markers = getTacticalMarkers(scenario.id);
  const routes = getTacticalRoutes(scenario.id);
  const zones = getDangerZones(scenario.id);
  const facts = [
    ["比赛时间", scenario.minute],
    ["当前比分", scenario.score],
    ["对手类型", scenario.opponent],
    ["曼联阵型", scenario.formation],
    ["球的位置", scenario.ballPosition],
    ["B费位置", scenario.brunoPosition],
    ["右边锋位置", scenario.rightWingerPosition],
    ["后腰保护", coverLabels[scenario.midfieldCover]],
    ["对方左边锋", scenario.opponentWinger],
    ["身后空间", spaceLabels[scenario.spaceBehind]],
    ["主要风险", scenario.mainRisk],
  ];

  return (
    <section className="scenario-panel">
      <div className="progress-row">
        <span>场景 {currentIndex + 1} / {total}</span>
        <span className={`mode-pill mode-${scenario.mode}`}>{modeName(scenario.mode)}</span>
      </div>

      <div className="pitch">
        <div className="pitch-line center-line" />
        <div className="pitch-line box-left" />
        <div className="pitch-line box-right" />
        <div className="space-lane">身后空间</div>
        {zones.map((zone) => (
          <div
            className={`danger-zone danger-${zone.level}`}
            key={zone.label}
            style={{
              left: `${zone.x}%`,
              top: `${zone.y}%`,
              width: `${zone.width}%`,
              height: `${zone.height}%`,
            }}
          >
            {zone.label}
          </div>
        ))}
        {routes.map((route) => (
          <span
            className={`route route-${route.kind}`}
            key={route.label}
            style={{
              left: `${route.x}%`,
              top: `${route.y}%`,
              width: `${route.length}%`,
              transform: `rotate(${route.angle}deg)`,
            }}
          >
            {route.label}
          </span>
        ))}
        {markers.map((marker) => (
          <span
            className={`marker marker-${marker.team}`}
            key={`${marker.label}-${marker.x}-${marker.y}`}
            style={{ left: `${marker.x}%`, top: `${marker.y}%` }}
            title={marker.note}
          >
            {marker.label}
          </span>
        ))}
      </div>

      <dl className="fact-grid">
        {facts.map(([label, value]) => (
          <div key={label} className="fact-item">
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>

      <p className="description">{scenario.description}</p>
      <h2>{scenario.question}</h2>
    </section>
  );
}

type TacticalMarker = {
  label: string;
  team: "united" | "opponent" | "ball";
  x: number;
  y: number;
  note: string;
};

type TacticalRoute = {
  label: string;
  kind: "run" | "pass" | "risk";
  x: number;
  y: number;
  length: number;
  angle: number;
};

type DangerZone = {
  label: string;
  level: "warning" | "danger";
  x: number;
  y: number;
  width: number;
  height: number;
};

function getTacticalMarkers(id: number): TacticalMarker[] {
  const maps: Record<number, TacticalMarker[]> = {
    1: [
      marker("球", "ball", 62, 54, "B费刚接到二点球"),
      marker("达洛特", "united", 74, 70, "延迟启动点"),
      marker("B费", "united", 60, 48, "右半空间持球"),
      marker("RW", "united", 86, 28, "贴边拉宽"),
      marker("DM", "united", 45, 62, "后腰保护到位"),
      marker("LB", "opponent", 82, 31, "被右边锋牵制"),
      marker("LW", "opponent", 70, 82, "回追但转身慢"),
    ],
    2: [
      marker("球", "ball", 82, 25, "对方左边锋持球"),
      marker("达洛特", "united", 73, 34, "防内切角度"),
      marker("RW", "united", 86, 46, "身后追防"),
      marker("DM", "united", 48, 58, "保护不足"),
      marker("RCB", "united", 57, 43, "不能被迫横移"),
      marker("LW", "opponent", 84, 24, "右脚内切爆点"),
      marker("ST", "opponent", 54, 31, "牵制中卫"),
    ],
    3: [
      marker("球", "ball", 58, 64, "右中卫出球受压"),
      marker("达洛特", "united", 62, 48, "内收接应点"),
      marker("RCB", "united", 55, 65, "被迫横传"),
      marker("B费", "united", 45, 34, "被后腰盯住"),
      marker("RW", "united", 86, 33, "边线脚下点"),
      marker("LW", "opponent", 72, 58, "切断回传线路"),
      marker("CM", "opponent", 50, 45, "封锁中路"),
    ],
    4: [
      marker("球", "ball", 39, 40, "禁区前二点"),
      marker("达洛特", "united", 68, 73, "远端保护位"),
      marker("B费", "united", 43, 38, "抢二点"),
      marker("RW", "united", 66, 24, "远端禁区内"),
      marker("DM", "united", 50, 65, "回追中"),
      marker("LW", "opponent", 84, 78, "已在身后启动"),
      marker("ST", "opponent", 52, 54, "准备反击接应"),
    ],
    5: [
      marker("球", "ball", 82, 38, "右边锋背身接球"),
      marker("达洛特", "united", 76, 51, "倒三角接应位"),
      marker("B费", "united", 65, 43, "肋部做墙"),
      marker("RW", "united", 86, 35, "被贴身"),
      marker("DM", "united", 49, 60, "保护良好"),
      marker("LB", "opponent", 88, 36, "贴住右边锋"),
      marker("LW", "opponent", 75, 67, "回收到禁区边"),
    ],
    6: [
      marker("球", "ball", 82, 27, "对方边锋正面持球"),
      marker("达洛特", "united", 73, 36, "保持距离延缓"),
      marker("RW", "united", 82, 47, "外侧夹击"),
      marker("B费", "united", 51, 53, "第二线保护"),
      marker("RCB", "united", 58, 39, "禁区内保护"),
      marker("LW", "opponent", 84, 26, "爆点边锋"),
      marker("ST", "opponent", 47, 30, "等传中"),
    ],
    7: [
      marker("球", "ball", 56, 66, "右中卫接门将短传"),
      marker("达洛特", "united", 62, 52, "双枢纽接应"),
      marker("RCB", "united", 55, 66, "第一线出球"),
      marker("B费", "united", 42, 35, "偏左牵制后腰"),
      marker("RW", "united", 87, 31, "高位贴边"),
      marker("LW", "opponent", 69, 54, "偏内反抢"),
      marker("ST", "opponent", 51, 57, "影子覆盖后腰"),
    ],
    8: [
      marker("球", "ball", 72, 55, "达洛特抢回球"),
      marker("达洛特", "united", 70, 56, "第一脚处理"),
      marker("B费", "united", 51, 35, "中路前插"),
      marker("RW", "united", 84, 25, "冲对方身后"),
      marker("DM", "united", 50, 67, "转换保护"),
      marker("LW", "opponent", 73, 62, "就地反抢"),
      marker("LB", "opponent", 86, 36, "站位过高"),
    ],
    9: [
      marker("球", "ball", 37, 35, "左中卫准备长传"),
      marker("达洛特", "united", 69, 70, "提前回撤占落点"),
      marker("RW", "united", 78, 50, "回防距离远"),
      marker("RCB", "united", 56, 61, "补禁区"),
      marker("B费", "united", 47, 55, "中圈附近"),
      marker("LW", "opponent", 83, 74, "冲角旗区"),
      marker("LCB", "opponent", 36, 34, "长传发起"),
    ],
    10: [
      marker("球", "ball", 64, 43, "B费准备传中或直塞"),
      marker("达洛特", "united", 76, 67, "延迟套边起点"),
      marker("B费", "united", 63, 42, "右半空间正脚"),
      marker("RW", "united", 72, 29, "内收带走左后卫"),
      marker("DM", "united", 47, 66, "保护偏薄"),
      marker("LB", "opponent", 71, 31, "被带入禁区边"),
      marker("LW", "opponent", 84, 76, "反击速度快"),
    ],
  };

  return maps[id] ?? maps[1];
}

function getTacticalRoutes(id: number): TacticalRoute[] {
  const maps: Record<number, TacticalRoute[]> = {
    1: [route("延迟外插", "run", 74, 63, 17, -58), route("倒三角", "pass", 63, 52, 18, -12)],
    2: [route("封内线", "run", 75, 34, 11, -20), route("内切威胁", "risk", 81, 26, 22, 156)],
    3: [route("内收接球", "run", 67, 53, 14, 162), route("出球角", "pass", 58, 63, 15, -28)],
    4: [route("反击斜长传", "risk", 52, 52, 36, 35), route("回撤保护", "run", 69, 66, 16, 98)],
    5: [route("做墙", "pass", 82, 39, 17, 167), route("倒三角位", "run", 78, 47, 12, 126)],
    6: [route("外侧夹击", "run", 80, 45, 11, -80), route("内切线", "risk", 82, 27, 22, 157)],
    7: [route("内收成双枢纽", "run", 67, 56, 12, 157), route("转移线路", "pass", 58, 63, 25, -38)],
    8: [route("直塞身后", "pass", 72, 53, 18, -56), route("延迟跟进", "run", 72, 56, 16, -38)],
    9: [route("长传落点", "risk", 39, 36, 45, 35), route("提前回撤", "run", 70, 64, 14, 94)],
    10: [route("可管理外插", "run", 76, 61, 17, -58), route("被断反击", "risk", 72, 67, 20, 34)],
  };

  return maps[id] ?? maps[1];
}

function getDangerZones(id: number): DangerZone[] {
  const maps: Record<number, DangerZone[]> = {
    1: [zone("外线窗口", "warning", 76, 18, 21, 34)],
    2: [zone("内切射门区", "danger", 58, 18, 25, 26)],
    3: [zone("边线压迫陷阱", "danger", 77, 42, 20, 34)],
    4: [zone("远端身后", "danger", 72, 60, 25, 30)],
    5: [zone("倒三角空间", "warning", 62, 42, 20, 22)],
    6: [zone("内线禁区口", "danger", 57, 22, 25, 28)],
    7: [zone("中路接应口", "warning", 55, 45, 17, 22)],
    8: [zone("纵深空间", "warning", 77, 15, 20, 28)],
    9: [zone("长传身后", "danger", 70, 58, 25, 32)],
    10: [zone("末段反击口", "danger", 74, 61, 23, 31)],
  };

  return maps[id] ?? maps[1];
}

function marker(
  label: string,
  team: TacticalMarker["team"],
  x: number,
  y: number,
  note: string,
): TacticalMarker {
  return { label, team, x, y, note };
}

function route(
  label: string,
  kind: TacticalRoute["kind"],
  x: number,
  y: number,
  length: number,
  angle: number,
): TacticalRoute {
  return { label, kind, x, y, length, angle };
}

function zone(
  label: string,
  level: DangerZone["level"],
  x: number,
  y: number,
  width: number,
  height: number,
): DangerZone {
  return { label, level, x, y, width, height };
}

function modeName(mode: Scenario["mode"]) {
  const names = {
    defense: "防守 1v1",
    overlap: "套边时机",
    invert: "内收接应",
    transition: "防反击",
  };

  return names[mode];
}
