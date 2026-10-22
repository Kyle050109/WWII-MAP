# 烽火欧陆 · WWII Europe Map

**简体中文** · [English](README_EN.md)

第二次世界大战欧洲战场互动地图（1939年9月1日 — 1945年5月8日）。拖动时间轴，看战线推移、攻势展开与重大事件。界面支持中英双语。

灵感来自 [江山时序 jiangshan-map](https://github.com/DeanChensj/jiangshan-map)。

## 功能

- **时间轴**：可拖动或自动播放（0.5× – 4×），分为 8 个阶段，从“闪电战”到“第三帝国覆灭”。
- **版图快照**：35 个时间点的控制区，包括吞并区、德占区、维希法国、轴心国盟友、游击队解放区和中立国。
- **战线**：东线、西线、意大利和南斯拉夫战线，并以虚线显示上一阶段的战线，方便对比推进幅度。
- **攻势箭头**：97 条主要作战行动的箭头，随战役进程逐渐延伸。
- **包围圈**：列宁格勒、斯大林格勒、阿登突出部、鲁尔、柏林等。
- **重大事件**：93 个事件，涵盖战役、空战、海战、政治事件、起义与暴行。点击事件会跳到当天并定位到发生地。
- **其他**：中英文切换、浅色/深色主题、手机适配、悬停图例高亮对应势力。

### 快捷键

| 按键 | 作用 |
|---|---|
| 空格 | 播放 / 暂停 |
| ← / → | 上一个 / 下一个事件 |
| Shift + ← / → | 前后跳一个月 |
| Esc | 关闭事件卡片 |

在网址末尾加 `#日期` 可直接跳到某一天，例如 `index.html#1942-11-19`。

## 使用

用浏览器直接打开 `index.html` 即可。需要联网，因为页面会从 CDN 加载 D3 和 Google Fonts。

也可以用 GitHub Pages 发布：进入仓库 **Settings → Pages**，Source 选 **Deploy from a branch**，分支选 `main`、目录选 `/ (root)`。几分钟后可通过 `https://kyle050109.github.io/WWII-MAP/` 访问。

## 项目结构

```
index.html          构建产物，可直接打开
src/template.html   页面结构、样式与交互代码
src/fronts.js       控制状态、版图快照、战线与控制区
src/events.js       阶段、事件、攻势箭头、城市与地名
data/geo.json       1938 年国界、河流、湖泊（已裁剪）
scripts/build.py    把以上文件合并成 index.html
scripts/prep.py     从原始 GeoJSON 生成 data/geo.json
```

修改 `src/` 或 `data/` 后，运行以下命令重新生成 `index.html`：

```bash
python3 scripts/build.py
```

### 数据格式

- 坐标一律为 `[经度, 纬度]`。
- `fronts.js` 中：
  - `D.base` 记录每个 1938 年国家的控制状态随时间的变化；
  - `D.staticZones` 是跨越多个快照的分区，如维希法国、克罗地亚独立国；
  - `D.fronts[n]` 是第 n 个快照的战线区域。
- 控制状态代码：

| 代码 | 含义 |
|---|---|
| `reich` | 纳粹德国及吞并区 |
| `occ` | 德军占领区 |
| `it` | 意大利及其占领区 |
| `minor` | 轴心国盟友 |
| `vichy` | 维希法国 |
| `al` | 西方盟国 |
| `su` | 苏联及东线解放区 |
| `lib` | 游击队解放区 |
| `neu` | 中立国 |

## 说明

控制区与战线为示意性近似，按时间快照手工绘制，并非精确测绘边界。两次快照之间，地图上的版图保持不变。

## 数据来源

- 1938 年国界：[aourednik/historical-basemaps](https://github.com/aourednik/historical-basemaps)（GPL-3.0）
- 河流与湖泊：[Natural Earth](https://www.naturalearthdata.com/)（公有领域）
- 渲染：[D3.js](https://d3js.org/)
