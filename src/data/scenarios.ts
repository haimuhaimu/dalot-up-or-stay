import type { Scenario } from "../types/game";

export const scenarios: Scenario[] = [
  {
    id: 1,
    mode: "overlap",
    minute: "12'",
    score: "曼联 0-0 布莱顿",
    opponent: "高位压迫型",
    formation: "4-2-3-1",
    ballPosition: "右肋部，B费刚接到二点球",
    brunoPosition: "右半空间，面向前场",
    rightWingerPosition: "贴边拉宽，吸住对方左后卫",
    midfieldCover: "good",
    opponentWinger: "回防积极但转身慢",
    spaceBehind: "medium",
    mainRisk: "套边太早会把传球线路带死",
    description:
      "曼联完成一次反抢，布莱顿左路防线还没完全落位。右边锋保持宽度，B费抬头观察，但身前没有直接纵向传球口。",
    question: "这球你要怎么处理？",
    options: [
      {
        id: "delay-overlap",
        label: "延迟套边",
        score: 94,
        isBest: true,
        explanation:
          "先停在 B费外侧身后半步，等右边锋牵制住左后卫再突然加速，能同时打开下底和倒三角线路。",
        impact: { attack: 28, defense: 18, space: 27, teamwork: 21 },
      },
      {
        id: "sprint-overlap",
        label: "高速套边",
        score: 78,
        isBest: false,
        explanation:
          "推进意图很清楚，但启动过早会让对手提前退防，B费的持球角度反而被压缩。",
        impact: { attack: 27, defense: 12, space: 18, teamwork: 21 },
      },
      {
        id: "invert-support",
        label: "内收接应",
        score: 66,
        isBest: false,
        explanation:
          "能帮中路稳住球权，但此刻右边已经形成局部人数优势，内收会错过边路突破窗口。",
        impact: { attack: 14, defense: 20, space: 16, teamwork: 16 },
      },
      {
        id: "stay-back",
        label: "留后防反击",
        score: 58,
        isBest: false,
        explanation:
          "安全性不错，但后腰保护到位，完全不上会让曼联少一个能改变纵深的跑动点。",
        impact: { attack: 8, defense: 27, space: 11, teamwork: 12 },
      },
    ],
  },
  {
    id: 2,
    mode: "defense",
    minute: "27'",
    score: "曼联 1-0 纽卡斯尔",
    opponent: "快速转换型",
    formation: "4-2-3-1",
    ballPosition: "对方左边锋在边线附近持球",
    brunoPosition: "前场中路，来不及回收",
    rightWingerPosition: "刚丢球，身后追防",
    midfieldCover: "poor",
    opponentWinger: "爆发力强，喜欢内切打远角",
    spaceBehind: "large",
    mainRisk: "被一步过掉后中卫必须横移，禁区弧顶会空",
    description:
      "曼联右路进攻丢球，对手立刻把球交到左边锋脚下。你身后空间很大，后腰还在回追路上。",
    question: "这球你要怎么处理？",
    options: [
      {
        id: "show-outside",
        label: "放外线防内切",
        score: 96,
        isBest: true,
        explanation:
          "对方最强武器是内切射门。你要用身体角度封住内线，宁愿让他走外线传中，也别让中路被打穿。",
        impact: { attack: 4, defense: 34, space: 30, teamwork: 28 },
      },
      {
        id: "press-hard",
        label: "前压逼抢",
        score: 44,
        isBest: false,
        explanation:
          "后腰保护不足时贸然上抢，一旦被趟过就是清晰的禁区前沿机会。",
        impact: { attack: 8, defense: 9, space: 10, teamwork: 17 },
      },
      {
        id: "delay",
        label: "保持距离延缓",
        score: 86,
        isBest: false,
        explanation:
          "这是可接受选择，能等队友回位；但如果不给出明确的防内切身体方向，对手仍会获得强侧脚机会。",
        impact: { attack: 3, defense: 29, space: 25, teamwork: 29 },
      },
      {
        id: "tactical-foul",
        label: "战术犯规",
        score: 62,
        isBest: false,
        explanation:
          "可以阻断转换，但位置还靠边，优先用站位解决，不必过早吃牌。",
        impact: { attack: 1, defense: 25, space: 20, teamwork: 16 },
      },
    ],
  },
  {
    id: 3,
    mode: "invert",
    minute: "34'",
    score: "曼联 0-1 阿森纳",
    opponent: "中路压迫型",
    formation: "4-3-3",
    ballPosition: "中卫右侧持球，被迫横传",
    brunoPosition: "前腰线，被后腰盯住",
    rightWingerPosition: "站在边线，准备接脚下球",
    midfieldCover: "average",
    opponentWinger: "站位偏高，切断回传中卫线路",
    spaceBehind: "small",
    mainRisk: "后场出球被锁在边线",
    description:
      "阿森纳压迫触发点很清楚：球到右中卫就封边线。边路没有纵深空间，但中路六号位旁边出现短暂接应空当。",
    question: "这球你要怎么处理？",
    options: [
      {
        id: "invert",
        label: "内收接应",
        score: 98,
        isBest: true,
        explanation:
          "内收成临时中场，能给右中卫一个向内的传球角度，并帮助曼联绕开对方边线压迫陷阱。",
        impact: { attack: 22, defense: 24, space: 30, teamwork: 22 },
      },
      {
        id: "overlap",
        label: "高速套边",
        score: 39,
        isBest: false,
        explanation:
          "身后空间小、边路被锁死，此时套边更像主动跑进死胡同。",
        impact: { attack: 11, defense: 8, space: 7, teamwork: 13 },
      },
      {
        id: "stay",
        label: "留后防反击",
        score: 63,
        isBest: false,
        explanation:
          "能保守站住位置，但解决不了出球角度问题，压力会继续留在右中卫身上。",
        impact: { attack: 8, defense: 25, space: 13, teamwork: 17 },
      },
      {
        id: "triangle",
        label: "倒三角接应",
        score: 75,
        isBest: false,
        explanation:
          "如果队友能第一时间做墙，这是不错的保险选择；但最优解仍是更主动地内收到中场线。",
        impact: { attack: 17, defense: 21, space: 18, teamwork: 19 },
      },
    ],
  },
  {
    id: 4,
    mode: "transition",
    minute: "41'",
    score: "曼联 1-1 热刺",
    opponent: "反击冲刺型",
    formation: "4-2-3-1",
    ballPosition: "曼联左路传中被解围，球落到禁区前",
    brunoPosition: "禁区弧顶抢二点",
    rightWingerPosition: "远端禁区内等二点",
    midfieldCover: "poor",
    opponentWinger: "速度极快，已经在你身后启动",
    spaceBehind: "large",
    mainRisk: "远端丢二点后被直接打身后",
    description:
      "这是最容易上头的瞬间：你看到禁区外有二点球机会，但身后已经有人准备冲刺，后腰位置又空。",
    question: "这球你要怎么处理？",
    options: [
      {
        id: "stay-transition",
        label: "留后防反击",
        score: 97,
        isBest: true,
        explanation:
          "远端边后卫必须读到反击链条。你留在中线附近能切断第一脚斜长传，防止整条防线被拉开。",
        impact: { attack: 7, defense: 35, space: 29, teamwork: 26 },
      },
      {
        id: "press-second-ball",
        label: "前压逼抢",
        score: 52,
        isBest: false,
        explanation:
          "如果抢不到第一下，身后就是大片草地。后腰保护差时，这个风险太高。",
        impact: { attack: 17, defense: 9, space: 8, teamwork: 18 },
      },
      {
        id: "delayed-overlap",
        label: "延迟套边",
        score: 46,
        isBest: false,
        explanation:
          "曼联进攻已经到收尾阶段，这时套边参与价值很低，防反责任更重要。",
        impact: { attack: 12, defense: 10, space: 8, teamwork: 16 },
      },
      {
        id: "call-cover",
        label: "呼叫协防",
        score: 80,
        isBest: false,
        explanation:
          "沟通是必要的，但不能只喊不动。你自己也要先占住防反击线路。",
        impact: { attack: 5, defense: 27, space: 23, teamwork: 25 },
      },
    ],
  },
  {
    id: 5,
    mode: "overlap",
    minute: "53'",
    score: "曼联 0-0 埃弗顿",
    opponent: "低位密集型",
    formation: "4-2-3-1",
    ballPosition: "右边锋背身接球，边线附近",
    brunoPosition: "右肋部等待撞墙",
    rightWingerPosition: "被左后卫贴身，无法转身",
    midfieldCover: "good",
    opponentWinger: "回收到禁区边，注意力在球",
    spaceBehind: "small",
    mainRisk: "没有第三人跑动，右路会被困死",
    description:
      "对手阵型压得很低，边路一对一没有空间。B费在肋部可以做墙，右边锋需要你带走防守者。",
    question: "这球你要怎么处理？",
    options: [
      {
        id: "underlap-triangle",
        label: "倒三角接应",
        score: 92,
        isBest: true,
        explanation:
          "低位防守前，盲目下底不如占住倒三角位置。你能给边锋回做出口，也能接 B费的短传再传中。",
        impact: { attack: 27, defense: 18, space: 25, teamwork: 22 },
      },
      {
        id: "sprint",
        label: "高速套边",
        score: 73,
        isBest: false,
        explanation:
          "能制造拉扯，但身后空间小、对方落位完整，下底质量未必高。",
        impact: { attack: 25, defense: 12, space: 16, teamwork: 20 },
      },
      {
        id: "stay",
        label: "留后防反击",
        score: 55,
        isBest: false,
        explanation:
          "太保守了。后腰保护不错，面对低位防守需要边后卫提供第三人接应。",
        impact: { attack: 7, defense: 27, space: 9, teamwork: 12 },
      },
      {
        id: "press",
        label: "前压逼抢",
        score: 42,
        isBest: false,
        explanation:
          "曼联现在是控球方，不存在立刻逼抢的触发条件。",
        impact: { attack: 9, defense: 11, space: 8, teamwork: 14 },
      },
    ],
  },
  {
    id: 6,
    mode: "defense",
    minute: "61'",
    score: "曼联 2-1 切尔西",
    opponent: "边路爆点型",
    formation: "4-4-2 防守落位",
    ballPosition: "对方左边锋接到斜传，正面对你",
    brunoPosition: "回到中路第二线",
    rightWingerPosition: "已经回收到你身前五米",
    midfieldCover: "average",
    opponentWinger: "右脚将，喜欢先外拨再内切",
    spaceBehind: "medium",
    mainRisk: "过早下脚被变向穿裆",
    description:
      "你和右边锋已经形成二防一，但对手边锋脚下节奏好。禁区内有中锋等待传中，弧顶也有人包抄。",
    question: "这球你要怎么处理？",
    options: [
      {
        id: "delay-distance",
        label: "保持距离延缓",
        score: 93,
        isBest: true,
        explanation:
          "二防一时别急着赌博。你负责控制内线和节奏，让右边锋从外侧施压，逼对手把球交回去。",
        impact: { attack: 3, defense: 32, space: 28, teamwork: 30 },
      },
      {
        id: "tackle",
        label: "前压逼抢",
        score: 57,
        isBest: false,
        explanation:
          "有协防时可以施压，但正面对爆点边锋直接扑，会给他变向攻击身后的机会。",
        impact: { attack: 7, defense: 18, space: 12, teamwork: 20 },
      },
      {
        id: "show-out",
        label: "放外线防内切",
        score: 85,
        isBest: false,
        explanation:
          "方向正确，但还需要配合右边锋的外侧夹击，单纯放外线会让传中压力变大。",
        impact: { attack: 2, defense: 29, space: 25, teamwork: 29 },
      },
      {
        id: "foul",
        label: "战术犯规",
        score: 48,
        isBest: false,
        explanation:
          "局面还在可控范围，没必要送定位球。",
        impact: { attack: 1, defense: 18, space: 15, teamwork: 14 },
      },
    ],
  },
  {
    id: 7,
    mode: "invert",
    minute: "68'",
    score: "曼联 1-1 西汉姆",
    opponent: "双前锋压迫型",
    formation: "3-2-5 控球结构",
    ballPosition: "奥纳纳短传到右中卫",
    brunoPosition: "前腰线偏左，牵制对方后腰",
    rightWingerPosition: "高位贴边，压住左翼卫",
    midfieldCover: "good",
    opponentWinger: "站位偏内，想抢断后直塞",
    spaceBehind: "medium",
    mainRisk: "第一线出不来，被迫大脚失去球权",
    description:
      "曼联想从后场短传推进。右边锋已经把宽度拉满，你身前的内侧通道短暂打开，卡塞米罗被对方前锋影子覆盖。",
    question: "这球你要怎么处理？",
    options: [
      {
        id: "invert-pivot",
        label: "内收接应",
        score: 95,
        isBest: true,
        explanation:
          "你内收到后腰旁边，能形成双枢纽出球点。这样右中卫不用冒险直传边线，也保留转移到弱侧的可能。",
        impact: { attack: 23, defense: 25, space: 25, teamwork: 22 },
      },
      {
        id: "overlap",
        label: "高速套边",
        score: 51,
        isBest: false,
        explanation:
          "边锋已经占宽，你再外走会造成同线重叠，反而减少一个中路接应点。",
        impact: { attack: 13, defense: 13, space: 9, teamwork: 16 },
      },
      {
        id: "stay-centerback",
        label: "留后防反击",
        score: 74,
        isBest: false,
        explanation:
          "能保持三后卫保险，但当前更需要你向中场线移动，帮助第一线出球。",
        impact: { attack: 11, defense: 29, space: 16, teamwork: 18 },
      },
      {
        id: "call",
        label: "呼叫协防",
        score: 60,
        isBest: false,
        explanation:
          "沟通有帮助，但这个局面不是防守协防问题，而是出球结构需要你补位。",
        impact: { attack: 9, defense: 20, space: 14, teamwork: 17 },
      },
    ],
  },
  {
    id: 8,
    mode: "transition",
    minute: "74'",
    score: "曼联 2-2 利物浦",
    opponent: "高压反抢型",
    formation: "4-2-3-1",
    ballPosition: "右路刚抢回球，球在你脚下",
    brunoPosition: "中路前插，示意要斜传",
    rightWingerPosition: "身前启动，准备冲身后",
    midfieldCover: "average",
    opponentWinger: "反抢凶，身后留下空当",
    spaceBehind: "large",
    mainRisk: "第一脚处理慢会被围抢",
    description:
      "你抢断成功后有两秒窗口。对方边锋还在你身边反抢，但他们左后卫站位很高，右路纵深空间巨大。",
    question: "这球你要怎么处理？",
    options: [
      {
        id: "release-winger",
        label: "高速套边",
        score: 88,
        isBest: false,
        explanation:
          "你可以带一步冲出去，但最佳处理是更早把球送到右边锋身前，让他攻击最大空间。",
        impact: { attack: 30, defense: 12, space: 24, teamwork: 22 },
      },
      {
        id: "quick-support",
        label: "延迟套边",
        score: 96,
        isBest: true,
        explanation:
          "先把球交给右边锋攻击身后，再从内侧延迟跟进。这样既利用纵深，也保留倒三角二次接应。",
        impact: { attack: 32, defense: 16, space: 27, teamwork: 21 },
      },
      {
        id: "invert-safe",
        label: "内收接应",
        score: 69,
        isBest: false,
        explanation:
          "能躲开反抢，但会放慢一次很好的转换机会。",
        impact: { attack: 14, defense: 23, space: 15, teamwork: 17 },
      },
      {
        id: "foul",
        label: "战术犯规",
        score: 25,
        isBest: false,
        explanation:
          "你已经抢到球了，犯规会把一次进攻窗口白白送掉。",
        impact: { attack: 0, defense: 10, space: 5, teamwork: 10 },
      },
    ],
  },
  {
    id: 9,
    mode: "defense",
    minute: "82'",
    score: "曼联 1-0 狼队",
    opponent: "长传冲吊型",
    formation: "5-4-1 防守收缩",
    ballPosition: "对方左中卫准备长传到你身后",
    brunoPosition: "回到中圈附近",
    rightWingerPosition: "体能下降，回防距离较远",
    midfieldCover: "average",
    opponentWinger: "身材强壮，擅长背身护球",
    spaceBehind: "large",
    mainRisk: "领先阶段被长传打到角旗区，连续承受传中",
    description:
      "比赛进入最后十分钟，对方开始频繁长传找左路。你刚才参与了一次进攻，回位速度决定这波防守质量。",
    question: "这球你要怎么处理？",
    options: [
      {
        id: "drop-early",
        label: "留后防反击",
        score: 94,
        isBest: true,
        explanation:
          "领先阶段识别长传预兆很重要。提前回撤占住落点内侧，能避免被迫朝自家球门奔跑。",
        impact: { attack: 4, defense: 35, space: 29, teamwork: 26 },
      },
      {
        id: "press-cb",
        label: "前压逼抢",
        score: 58,
        isBest: false,
        explanation:
          "距离太远，压不上就会给对手更轻松的长传脚法。",
        impact: { attack: 8, defense: 18, space: 13, teamwork: 19 },
      },
      {
        id: "show-out",
        label: "放外线防内切",
        score: 76,
        isBest: false,
        explanation:
          "落点到来后这是正确原则，但第一步应该先回撤到能争落点的位置。",
        impact: { attack: 3, defense: 27, space: 22, teamwork: 24 },
      },
      {
        id: "overlap",
        label: "高速套边",
        score: 22,
        isBest: false,
        explanation:
          "这个时间和比分还继续前插，等于把对方最想打的空间主动交出去。",
        impact: { attack: 10, defense: 2, space: 3, teamwork: 7 },
      },
    ],
  },
  {
    id: 10,
    mode: "overlap",
    minute: "89'",
    score: "曼联 1-1 阿斯顿维拉",
    opponent: "紧凑中位防守型",
    formation: "4-2-4 末段抢分",
    ballPosition: "右肋部，B费准备传中或直塞",
    brunoPosition: "右半空间，正脚能送身后",
    rightWingerPosition: "内收到禁区边，带走左后卫",
    midfieldCover: "poor",
    opponentWinger: "不太回防，但反击速度快",
    spaceBehind: "large",
    mainRisk: "最后阶段失误后被反击绝杀",
    description:
      "曼联想抢三分，右边锋内收带出了外线通道。全场都想喊你上，但后腰保护已经很薄，身后空间也非常大。",
    question: "这球你要怎么处理？",
    options: [
      {
        id: "measured-overlap",
        label: "延迟套边",
        score: 91,
        isBest: true,
        explanation:
          "可以上，但要等 B费控稳球、弱侧队友压住二点后再启动。最后阶段不是不能冒险，而是要冒可管理的险。",
        impact: { attack: 27, defense: 20, space: 23, teamwork: 21 },
      },
      {
        id: "all-out",
        label: "高速套边",
        score: 70,
        isBest: false,
        explanation:
          "能制造威胁，但你把身后空间完全交出。若传球被断，曼联会面对非常危险的反击。",
        impact: { attack: 31, defense: 6, space: 14, teamwork: 19 },
      },
      {
        id: "stay",
        label: "留后防反击",
        score: 82,
        isBest: false,
        explanation:
          "稳妥但偏保守。平局末段需要你提供外线威胁，只是启动时机要更克制。",
        impact: { attack: 10, defense: 32, space: 22, teamwork: 18 },
      },
      {
        id: "invert",
        label: "内收接应",
        score: 74,
        isBest: false,
        explanation:
          "能保护中路反抢，但会减少外线传中点，让 B费的选择变少。",
        impact: { attack: 16, defense: 25, space: 17, teamwork: 16 },
      },
    ],
  },
];
