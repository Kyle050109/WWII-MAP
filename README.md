# 烽火欧陆 · WWII Europe Map

第二次世界大战欧洲战场互动地图（1939.9.1 – 1945.5.8）。拖动时间轴，查看战线推移、攻势展开与重大事件，中英双语。

An interactive map of the Second World War in Europe, 1939–1945, in Chinese and English.

灵感来自 [江山时序 jiangshan-map](https://github.com/DeanChensj/jiangshan-map)。

## 功能

- **时间轴**：拖动、播放（0.5× – 4×），按 8 个阶段划分，从“闪电战”到“第三帝国覆灭”。
- **版图快照**：35 个时间点的控制区，包括吞并区、德占区、维希法国、轴心国盟友、游击队解放区和中立国。
- **战线**：东线、西线、意大利、南斯拉夫战线，以及上一阶段战线的虚线对比。
- **攻势箭头**：约 90 条主要作战行动，箭头随战役进程逐渐延伸。
- **包围圈**：列宁格勒、斯大林格勒、阿登突出部、鲁尔、柏林等。
- **重大事件**：约 90 个，涵盖战役、空战、海战、政治事件、起义与暴行，点击可跳转并定位。
- **其他**：中英文切换、浅色/深色主题、手机适配、图例悬停高亮。

### 快捷键

| 按键 | 作用 |
|---|---|
| 空格 | 播放 / 暂停 |
| ← / → | 上一个 / 下一个事件 |
| Shift + ← / → | 前后跳一个月 |
| Esc | 关闭事件卡片 |

可以用网址末尾的 `#日期` 直接跳到某一天，例如 `index.html#1942-11-19`。

## 使用

直接用浏览器打开 `index.html` 即可（需联网，从 CDN 加载 D3 和 Google Fonts）。

也可以开启 GitHub Pages：仓库 **Settings → Pages → Branch: `main` / root**，几分钟后访问
`https://kyle050109.github.io/WWII-MAP/`。

## 项目结构

```
index.html          构建产物，可直接打开
src/template.html   页面结构、样式与交互代码
src/fronts.js       状态定义、版图快照、战线与控制区
src/events.js       阶段、事件、攻势箭头、城市与地名
data/geo.json       1938 年国界、河流、湖泊（已裁剪简化）
scripts/build.py    把以上文件合并成 index.html
scripts/prep.py     从原始 GeoJSON 生成 data/geo.json
```

修改 `src/` 或 `data/` 后运行：

```bash
python3 scripts/build.py
```

### 数据格式速览

- 坐标一律为 `[经度, 纬度]`。
- `fronts.js` 中 `D.base` 记录每个 1938 年国家的状态随时间变化；`D.staticZones` 是跨多个快照的分区（如维希法国）；`D.fronts[n]` 是第 n 个快照的战线区域。
- 控制状态：`reich` 德国及吞并区、`occ` 德占区、`it` 意大利、`minor` 轴心盟友、`vichy` 维希法国、`al` 西方盟国、`su` 苏联、`lib` 游击队解放区、`neu` 中立国。

## 说明

控制区与战线为示意性近似，按时间快照手工绘制，并非精确测绘边界；两次快照之间版图保持不变。

## 数据来源

- 1938 年国界：[aourednik/historical-basemaps](https://github.com/aourednik/historical-basemaps)（GPL-3.0）
- 河流与湖泊：[Natural Earth](https://www.naturalearthdata.com/)（公有领域）
- 渲染：[D3.js](https://d3js.org/)
