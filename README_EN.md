# Europe Ablaze · WWII Europe Map

[简体中文](README.md) · **English**

An interactive map of the Second World War in Europe, from 1 September 1939 to 8 May 1945. Drag the timeline to watch the fronts move, offensives unfold and key events happen. The interface is available in Chinese and English.

## Features

- **Timeline**: drag it or let it play (0.5× – 4×). The war is divided into 8 phases, from Blitzkrieg to the Fall of the Reich.
- **Territorial snapshots**: control maps for 35 dates, showing annexed and occupied areas, Vichy France, Axis partners, partisan-liberated areas and neutral states.
- **Front lines**: the Eastern, Western, Italian and Yugoslav fronts, with the previous front shown as a dashed line so you can see how far it moved.
- **Offensive arrows**: 97 major operations, each arrow growing across the map as the campaign progresses.
- **Encirclements**: Leningrad, Stalingrad, the Bulge, the Ruhr, Berlin and others.
- **Key events**: 93 events covering battles, air and naval warfare, politics, uprisings and atrocities. Clicking an event jumps to that day and zooms to where it happened.
- **Also**: Chinese/English toggle, light and dark themes, mobile layout, and a legend that highlights each side's territory on hover.

### Keyboard shortcuts

| Key | Action |
|---|---|
| Space | Play / pause |
| ← / → | Previous / next event |
| Shift + ← / → | Jump back / forward one month |
| Esc | Close the event card |

Add `#date` to the URL to open a specific day, for example `index.html#1942-11-19`.

## Usage

Open `index.html` in a browser. An internet connection is needed, since the page loads D3 and Google Fonts from a CDN.

To publish with GitHub Pages: go to **Settings → Pages**, set Source to **Deploy from a branch**, choose `main` and `/ (root)`. After a few minutes the map is available at `https://kyle050109.github.io/WWII-MAP/`.

## Project structure

```
index.html          Built page, ready to open
src/template.html   Page markup, styles and interaction code
src/fronts.js       Control statuses, territorial snapshots, fronts and zones
src/events.js       Phases, events, offensive arrows, cities and place names
data/geo.json       1938 borders, rivers and lakes (clipped)
scripts/build.py    Combines the files above into index.html
scripts/prep.py     Generates data/geo.json from the source GeoJSON
```

After editing anything in `src/` or `data/`, rebuild `index.html` with:

```bash
python3 scripts/build.py
```

### Data format

- All coordinates are `[longitude, latitude]`.
- In `fronts.js`:
  - `D.base` records how each 1938 state's control status changes over time;
  - `D.staticZones` holds areas that span several snapshots, such as Vichy France or the Independent State of Croatia;
  - `D.fronts[n]` holds the front-line zones for snapshot n.
- Control status codes:

| Code | Meaning |
|---|---|
| `reich` | Nazi Germany & annexed territory |
| `occ` | German-occupied |
| `it` | Italy & Italian-held |
| `minor` | Axis partners |
| `vichy` | Vichy France |
| `al` | Western Allies |
| `su` | Soviet Union & Soviet-held |
| `lib` | Partisan-liberated |
| `neu` | Neutral |

## Note

Areas of control and front lines are schematic approximations, drawn by hand as dated snapshots. They are not surveyed borders. Between two snapshots, the map shows the earlier one.

## Data sources

- 1938 borders: [aourednik/historical-basemaps](https://github.com/aourednik/historical-basemaps) (GPL-3.0)
- Rivers and lakes: [Natural Earth](https://www.naturalearthdata.com/) (public domain)
- Rendering: [D3.js](https://d3js.org/)
