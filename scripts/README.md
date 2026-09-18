# 球队合影生成脚本

把单张球员立绘合成为球队合影与海报的本地图像流水线。脚本只在本地运行，不参与站点构建。

## 依赖

```bash
pip install pillow opencv-python numpy
```

`detect_faces.swift` 与 `detect_faces.m` 调用 macOS Vision 框架做人脸检测，仅在 macOS 上可用。

## 目录约定

- 输入：`fc26-ut-cards/` 下的球员立绘与素材
- 输出：`output/`，其中 `output/player_portraits/` 存放单人立绘

两个目录都不纳入版本控制：素材体积大，产物可由脚本重新生成。首次运行前需要自行准备 `fc26-ut-cards/`。

## 脚本说明

合成主流程：

| 脚本 | 作用 |
| --- | --- |
| `build_team_family_portrait.py` | 生成球队合影，处理羽化边缘与队徽叠加 |
| `build_team_family_portrait_fused.py` | 合影的融合版本，用连通域提取前景后再合成 |
| `build_team_portrait_poster.py` | 在合影基础上排版海报，含背景与文字层 |

面部修复与校正：

| 脚本 | 作用 |
| --- | --- |
| `restore_team_photo_faces.py` | 用级联检测定位合影与原图中的人脸，回贴清晰面部 |
| `refine_team_photo_faces_nongenerative.py` | 非生成式修复，按 LAB 中位数做肤色对齐 |
| `precision_refine_team_photo_faces.py` | 逐人微调面部区域，附加接触阴影 |

诊断与调试：

| 脚本 | 作用 |
| --- | --- |
| `diagnose_team_head_proportions.py` | 标注头部比例，排查合影中人物大小不一致 |
| `fix_team_photo_spacing.py` | 调整人物间距 |
| `test_player_cutouts.py` | 用棋盘格背景检查抠图边缘质量 |

## 运行

```bash
python3 scripts/build_team_family_portrait.py
python3 scripts/restore_team_photo_faces.py
python3 scripts/build_team_portrait_poster.py
```

按需单独运行诊断脚本查看中间结果。
