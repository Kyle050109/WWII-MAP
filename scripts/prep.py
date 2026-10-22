"""Extract a European window from the 1938 historical basemap + Natural Earth rivers/lakes.
Output: build/geo.json  {countries:{id:{n,mp}}, rivers:[...], lakes:[...]}
Coordinates rounded to 2 decimals (keeps shared border vertices identical).
"""
import json, sys

HB = sys.argv[1]
NE = sys.argv[2]
OUT = sys.argv[3]

W, S, E, N = -26.0, 27.0, 62.0, 74.0


def clip_ring(ring):
    """Sutherland-Hodgman clip of a ring against the lon/lat rectangle."""
    def clip(pts, inside, inter):
        out = []
        if not pts:
            return out
        prev = pts[-1]
        for cur in pts:
            if inside(cur):
                if not inside(prev):
                    out.append(inter(prev, cur))
                out.append(cur)
            elif inside(prev):
                out.append(inter(prev, cur))
            prev = cur
        return out

    def ix(x):
        return lambda a, b: (x, a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0]))

    def iy(y):
        return lambda a, b: (a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]), y)

    pts = [tuple(p[:2]) for p in ring]
    if pts and pts[0] == pts[-1]:
        pts = pts[:-1]
    pts = clip(pts, lambda p: p[0] >= W, ix(W))
    pts = clip(pts, lambda p: p[0] <= E, ix(E))
    pts = clip(pts, lambda p: p[1] >= S, iy(S))
    pts = clip(pts, lambda p: p[1] <= N, iy(N))
    return pts


def rnd(pts):
    out = []
    for x, y in pts:
        q = (round(x, 2), round(y, 2))
        if not out or out[-1] != q:
            out.append(q)
    if len(out) > 1 and out[0] == out[-1]:
        out.pop()
    return out


def area(r):
    a = 0
    for i in range(len(r)):
        x1, y1 = r[i]
        x2, y2 = r[(i + 1) % len(r)]
        a += x1 * y2 - x2 * y1
    return a / 2


def polys(geom):
    if geom['type'] == 'Polygon':
        return [geom['coordinates']]
    if geom['type'] == 'MultiPolygon':
        return geom['coordinates']
    return []


ID = {
    'Germany': 'DEU', 'Poland': 'POL', 'France': 'FRA', 'United Kingdom': 'GBR', 'Ireland': 'IRL',
    'USSR': 'SUN', 'Armenia': 'SUN', 'Italy': 'ITA', 'Spain': 'ESP', 'Portugal': 'PRT', 'Switzerland': 'CHE',
    'Belgium': 'BEL', 'Netherlands': 'NLD', 'Luxembourg': 'LUX', 'Denmark': 'DNK', 'Norway': 'NOR',
    'Sweden': 'SWE', 'Finland': 'FIN', 'Estonia': 'EST', 'Latvia': 'LVA', 'Lithuania': 'LTU',
    'Czechoslovakia': 'CSK', 'Hungary': 'HUN', 'Romania': 'ROU', 'Bulgaria': 'BGR', 'Yugoslavia': 'YUG',
    'Albania': 'ALB', 'Greece': 'GRC', 'Turkey': 'TUR', 'Iran': 'IRN', 'Syria (France)': 'SYR',
    'Mesopotamia (GB)': 'IRQ', 'Mandatory Palestine (GB)': 'PSE', 'Israel': None, 'Jordan': 'JOR',
    'Egypt': 'EGY', 'Libya': 'LBY', 'Tunisia': 'TUN', 'Algeria (France)': 'DZA', 'Morocco (France)': 'MAR',
    'Saudi Arabia': 'SAU', 'Hejaz': 'SAU', 'Andorra': None, 'Kuwait': None,
    'Emirate of Bin Shal\'an': 'SAU',
}


def island_owner(b):
    x0, y0, x1, y1 = b
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if cx < -6.3 and cy > 61:
        return 'DNK'  # Faroe
    if cx < 0 and cy > 53:
        return 'GBR'
    if 13 < cx < 14 and 54 < cy < 55:
        return 'DEU'  # Rügen
    if 21.5 < cx < 23.5 and 57.8 < cy < 59.2:
        return 'EST'  # Saaremaa/Hiiumaa
    if 19 < cx < 21 and 59.9 < cy < 60.5:
        return 'FIN'  # Åland
    return None


def bbox_of(geom):
    xs, ys = [], []
    for p in polys(geom):
        for r in p:
            for c in r:
                xs.append(c[0]); ys.append(c[1])
    return min(xs), min(ys), max(xs), max(ys)


hb = json.load(open(HB))
countries = {}
for f in hb['features']:
    name = f['properties'].get('NAME')
    if not f['geometry']:
        continue
    b = bbox_of(f['geometry'])
    if b[2] < W or b[0] > E or b[3] < S or b[1] > N:
        continue
    cid = ID.get(name) if name else island_owner(b)
    if name and name not in ID:
        print('unmapped', name, file=sys.stderr)
    if not cid:
        continue
    for p in polys(f['geometry']):
        rings = []
        for i, r in enumerate(p):
            c = rnd(clip_ring(r))
            if len(c) < 3 or abs(area(c)) < 0.004:
                continue
            rings.append([list(q) for q in c])
        if rings:
            countries.setdefault(cid, []).append(rings)

NAMES = {
    'DEU': ['德国', 'Germany'], 'POL': ['波兰', 'Poland'], 'FRA': ['法国', 'France'], 'GBR': ['英国', 'United Kingdom'],
    'IRL': ['爱尔兰', 'Ireland'], 'SUN': ['苏联', 'Soviet Union'], 'ITA': ['意大利', 'Italy'], 'ESP': ['西班牙', 'Spain'],
    'PRT': ['葡萄牙', 'Portugal'], 'CHE': ['瑞士', 'Switzerland'], 'BEL': ['比利时', 'Belgium'], 'NLD': ['荷兰', 'Netherlands'],
    'LUX': ['卢森堡', 'Luxembourg'], 'DNK': ['丹麦', 'Denmark'], 'NOR': ['挪威', 'Norway'], 'SWE': ['瑞典', 'Sweden'],
    'FIN': ['芬兰', 'Finland'], 'EST': ['爱沙尼亚', 'Estonia'], 'LVA': ['拉脱维亚', 'Latvia'], 'LTU': ['立陶宛', 'Lithuania'],
    'CSK': ['捷克斯洛伐克', 'Czechoslovakia'], 'HUN': ['匈牙利', 'Hungary'], 'ROU': ['罗马尼亚', 'Romania'],
    'BGR': ['保加利亚', 'Bulgaria'], 'YUG': ['南斯拉夫', 'Yugoslavia'], 'ALB': ['阿尔巴尼亚', 'Albania'],
    'GRC': ['希腊', 'Greece'], 'TUR': ['土耳其', 'Turkey'], 'IRN': ['伊朗', 'Iran'], 'SYR': ['叙利亚', 'Syria'],
    'IRQ': ['伊拉克', 'Iraq'], 'PSE': ['巴勒斯坦', 'Palestine'], 'JOR': ['外约旦', 'Transjordan'], 'EGY': ['埃及', 'Egypt'],
    'LBY': ['利比亚', 'Libya'], 'TUN': ['突尼斯', 'Tunisia'], 'DZA': ['阿尔及利亚', 'Algeria'], 'MAR': ['摩洛哥', 'Morocco'],
    'SAU': ['阿拉伯', 'Arabia'],
}

out_c = {k: {'n': NAMES[k], 'mp': v} for k, v in countries.items()}

# rivers
riv = json.load(open(NE + '/ne_50m_rivers_lake_centerlines.geojson'))
rivers = []
for f in riv['features']:
    g = f['geometry']
    lines = g['coordinates'] if g['type'] == 'MultiLineString' else [g['coordinates']]
    keep = []
    for ln in lines:
        seg = [c for c in ln if W <= c[0] <= E and S <= c[1] <= N]
        seg = rnd(seg)
        if len(seg) >= 2:
            keep.append([list(q) for q in seg])
    if keep:
        rivers.append({'n': f['properties'].get('name'), 'r': f['properties'].get('scalerank'), 'l': keep})

def dp(pts, tol):
    if len(pts) < 3:
        return pts
    import math
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1e-12
    best, bi = -1, 0
    for i in range(1, len(pts) - 1):
        x, y = pts[i]
        d = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / L
        if d > best:
            best, bi = d, i
    if best > tol:
        return dp(pts[:bi + 1], tol)[:-1] + dp(pts[bi:], tol)
    return [pts[0], pts[-1]]


EXTRA = {'Neman', 'Bug', 'Southern Bug', 'Prut', 'Desna', 'Donets', 'Maas', 'Mosel', 'Oka', 'Volkhov', 'Kuban',
         'Pripyat', 'Sava', 'Morava', 'Tevere', 'Weser', 'Warta', 'Vltava', 'Neris', 'Seym', 'Marne', 'Main', 'Inn'}
r10 = json.load(open(NE + '/ne_10m_rivers_lake_centerlines.geojson'))
for f in r10['features']:
    nm = f['properties'].get('name')
    if nm not in EXTRA:
        continue
    g = f['geometry']
    lines = g['coordinates'] if g['type'] == 'MultiLineString' else [g['coordinates']]
    keep = []
    for ln in lines:
        seg = [tuple(c[:2]) for c in ln if W <= c[0] <= 55 and 34 <= c[1] <= 70]
        seg = rnd(dp(seg, 0.02))
        if len(seg) >= 2:
            keep.append([list(q) for q in seg])
    if keep:
        rivers.append({'n': nm, 'r': 7, 'l': keep})

lk = json.load(open(NE + '/ne_50m_lakes.geojson'))
lakes = []
for f in lk['features']:
    b = bbox_of(f['geometry'])
    if b[2] < W or b[0] > E or b[3] < S or b[1] > N:
        continue
    if b[0] < -20 and b[2] < -20:
        continue
    if 'Reservoir' in (f['properties'].get('name') or ''):
        continue  # post-war reservoirs
    for p in polys(f['geometry']):
        r = rnd(clip_ring(p[0]))
        if len(r) >= 3 and abs(area(r)) > 0.01:
            lakes.append({'n': f['properties'].get('name'), 'p': [list(q) for q in r]})

json.dump({'countries': out_c, 'rivers': rivers, 'lakes': lakes}, open(OUT, 'w'), separators=(',', ':'), ensure_ascii=False)
print('countries', len(out_c), 'rivers', len(rivers), 'lakes', len(lakes))
print(sorted(set(r['n'] for r in rivers if r['n'])))
print([l['n'] for l in lakes])
