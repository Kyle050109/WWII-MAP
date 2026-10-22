# Europe Ablaze · WWII Europe Map

[简体中文](README.md) · **English**

An interactive map of the Second World War in Europe, from 1 September 1939 to 8 May 1945. Drag the timeline to watch the fronts move, offensives unfold and key events happen. The interface is available in Chinese and English.

> **New: [Pacific Ablaze](asia/)**, the war in Asia and the Pacific (7 July 1937 – 9 September 1945) in a strategy-game style. See the section below.

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

## Pacific Ablaze (Asia and the Pacific)

In the `asia/` folder; open `asia/index.html` in a browser. It runs from the Marco Polo Bridge Incident to the surrender in Nanjing, drawn like a grand-strategy game:

- **Province grid**: about 7,000 provinces recoloured by controller each day. Occupied territory is hatched and front lines are generated along province edges.
- **Detailed base map**: Natural Earth 1:10m borders and coastlines, merged into 1938 colonial units (British India, French Indochina, the Dutch East Indies and so on). You can zoom down to single islands, with a scale bar.
- **China in detail**: Japanese occupation stage by stage, Manchukuo (including Jehol), Mengjiang, the Eighth Route Army and New Fourth Army base areas, Ichi-Go, and the Soviet invasion of Manchuria.
- **Pacific**: the southern advance, island hopping, the Solomons and New Guinea, and Burma. Small islands get coloured markers showing who holds them.
- **104 events** shown as newspaper "extra" cards, **98 offensive arrows**, curved country names, five game speeds (keys 1–5) and notifications for major events during playback.

After editing `asia/src/`, run `cd asia && python3 scripts/build.py` to rebuild the page; `scripts/prep_asia.py` regenerates `asia/data/asia_geo.json` from the Natural Earth source data.

