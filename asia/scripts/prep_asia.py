"""Build the Asia-Pacific base map (data/asia_geo.json) from Natural Earth 10m.

- merges modern countries into 1938-era units (British India, French Indochina ...)
- unions each unit by cancelling shared edges, then simplifies shared arcs once
  so neighbouring units still meet exactly
- extracts Chinese provincial borders, rivers, lakes
- generates seed points for the province grid (Voronoi cells drawn in the browser)

usage: python3 -I prep_asia.py <natural-earth geojson dir> <world_1938.geojson> <out.json>
"""
import json, math, random, sys
from collections import defaultdict

NE, HB, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
W, S, E, N = 66.0, -48.0, 208.0, 62.0
TOL = 0.0045          # Douglas-Peucker tolerance for borders/coasts (deg)
MIN_AREA = 0.00012    # drop islands smaller than this (deg^2) unless whitelisted
random.seed(7)

# ---------------------------------------------------------------- geometry
def shift(c):
    x, y = c[0], c[1]
    if x < -20:
        x += 360
    return (x, y)

def clip_ring(pts):
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
        def f(a, b):
            if a > b:
                a, b = b, a
            return (x, a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0]))
        return f
    def iy(y):
        def f(a, b):
            if a > b:
                a, b = b, a
            return (a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]), y)
        return f
    if pts and pts[0] == pts[-1]:
        pts = pts[:-1]
    pts = clip(pts, lambda p: p[0] >= W, ix(W))
    pts = clip(pts, lambda p: p[0] <= E, ix(E))
    pts = clip(pts, lambda p: p[1] >= S, iy(S))
    pts = clip(pts, lambda p: p[1] <= N, iy(N))
    return pts

def rnd(pts, d=5):
    out = []
    for x, y in pts:
        q = (round(x, d), round(y, d))
        if not out or out[-1] != q:
            out.append(q)
    while len(out) > 1 and out[0] == out[-1]:
        out.pop()
    return out

def area(r):
    a = 0.0
    n = len(r)
    for i in range(n):
        x1, y1 = r[i]
        x2, y2 = r[(i + 1) % n]
        a += x1 * y2 - x2 * y1
    return a / 2

def polys(g):
    if g['type'] == 'Polygon':
        return [g['coordinates']]
    if g['type'] == 'MultiPolygon':
        return g['coordinates']
    return []

def dp(pts, tol):
    if len(pts) < 3:
        return list(pts)
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        (x1, y1), (x2, y2) = pts[a], pts[b]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        best, bi = -1.0, -1
        for i in range(a + 1, b):
            x, y = pts[i]
            if L == 0:
                d = math.hypot(x - x1, y - y1)
            else:
                d = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / L
            if d > best:
                best, bi = d, i
        if bi >= 0 and best > tol:
            keep[bi] = True
            stack.append((a, bi))
            stack.append((bi, b))
    return [p for p, k in zip(pts, keep) if k]

def pip(x, y, ring):
    c = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            c = not c
        j = i
    return c

def bbox(r):
    xs = [p[0] for p in r]; ys = [p[1] for p in r]
    return min(xs), min(ys), max(xs), max(ys)

# ---------------------------------------------------------------- units
UNIT = {
    'CHN': 'CHN', 'TWN': 'TWN', 'HKG': 'HKG', 'MAC': 'MAC', 'PRK': 'KOR', 'KOR': 'KOR', 'JPN': 'JPN',
    'MNG': 'MNG', 'RUS': 'SUN', 'KAZ': 'SUN', 'KGZ': 'SUN', 'TJK': 'SUN', 'UZB': 'SUN', 'TKM': 'SUN',
    'IND': 'IND', 'PAK': 'IND', 'BGD': 'IND', 'LKA': 'IND', 'MDV': 'IND', 'IOT': 'IND', 'KAS': 'IND', 'KAB': 'IND',
    'NPL': 'NPL', 'BTN': 'BTN', 'AFG': 'AFG', 'MMR': 'MMR', 'THA': 'THA', 'VNM': 'FIC', 'LAO': 'FIC', 'KHM': 'FIC',
    'MYS': 'MYS', 'SGP': 'MAL', 'BRN': 'NBO', 'IDN': 'DEI', 'TLS': 'TIM', 'PHL': 'PHL', 'PNG': 'PNG', 'SLB': 'SLB',
    'AUS': 'AUS', 'NZL': 'NZL', 'NCL': 'NCL', 'VUT': 'VUT', 'FJI': 'FJI', 'NRU': 'NRU', 'KIR': 'KIR', 'TUV': 'KIR',
    'MHL': 'MHL', 'FSM': 'FSM', 'PLW': 'PLW', 'MNP': 'MNP', 'GUM': 'GUM', 'UMI': 'UMI', 'USA': 'USA',
    'IOA': 'AUS', 'ATC': 'AUS', 'CSI': 'AUS', 'NFK': 'AUS', 'CNM': 'CHN', 'PGA': 'CHN', 'SCR': 'CHN', 'SPI': 'CHN',
    'WLF': 'FJI', 'IRN': 'IRN', 'CAN': None, 'BJN': None, 'WSM': 'FJI', 'ASM': 'FJI', 'TON': 'FJI',
}
NAMES = {
    'CHN': ['中国', 'China'], 'TWN': ['台湾', 'Taiwan'], 'HKG': ['香港', 'Hong Kong'], 'MAC': ['澳门', 'Macau'],
    'KOR': ['朝鲜', 'Korea'], 'JPN': ['日本', 'Japan'], 'MNG': ['蒙古', 'Mongolia'], 'SUN': ['苏联', 'Soviet Union'],
    'IND': ['英属印度', 'British India'], 'NPL': ['尼泊尔', 'Nepal'], 'BTN': ['不丹', 'Bhutan'], 'AFG': ['阿富汗', 'Afghanistan'],
    'IRN': ['伊朗', 'Iran'], 'MMR': ['缅甸', 'Burma'], 'THA': ['泰国', 'Thailand'], 'FIC': ['法属印度支那', 'French Indochina'],
    'MAL': ['马来亚', 'Malaya'], 'NBO': ['北婆罗洲', 'British Borneo'], 'DEI': ['荷属东印度', 'Dutch East Indies'],
    'TIM': ['葡属帝汶', 'Portuguese Timor'], 'PHL': ['菲律宾', 'Philippines'], 'PNG': ['新几内亚', 'New Guinea'],
    'SLB': ['所罗门群岛', 'Solomon Islands'], 'AUS': ['澳大利亚', 'Australia'], 'NZL': ['新西兰', 'New Zealand'],
    'NCL': ['新喀里多尼亚', 'New Caledonia'], 'VUT': ['新赫布里底', 'New Hebrides'], 'FJI': ['斐济', 'Fiji'],
    'NRU': ['瑙鲁', 'Nauru'], 'KIR': ['吉尔伯特群岛', 'Gilbert Islands'], 'MHL': ['马绍尔群岛', 'Marshall Islands'],
    'FSM': ['加罗林群岛', 'Caroline Islands'], 'PLW': ['帕劳', 'Palau'], 'MNP': ['马里亚纳群岛', 'Mariana Islands'],
    'GUM': ['关岛', 'Guam'], 'UMI': ['威克岛与中途岛', 'Wake & Midway'], 'USA': ['美国', 'United States'],
}

# islands that must keep their own cell even when small (lon, lat)
KEY_ISLANDS = [
    (166.63, 19.29), (177.37, 28.21), (145.75, 15.19), (145.63, 15.0), (144.78, 13.44), (141.32, 24.78),
    (142.19, 27.07), (134.24, 7.0), (134.49, 7.5), (134.15, 6.9), (167.73, 9.18), (167.47, 9.4), (162.35, 11.45),
    (171.38, 7.1), (172.98, 1.35), (172.95, 3.05), (173.0, 1.8), (173.18, 52.9), (177.55, 51.98), (160.05, -9.45),
    (160.15, -9.1), (157.35, -8.25), (155.5, -6.3), (147.2, -2.05), (136.1, -1.05), (135.5, -1.05), (128.4, 2.2),
    (117.6, 3.33), (115.23, 5.3), (127.0, 26.5), (128.2, 26.65), (124.2, 24.4), (151.8, 7.4), (151.85, 7.45),
    (138.1, 9.5), (165.95, -10.7), (167.0, -15.4), (130.5, -12.4), (149.0, -6.2), (152.2, -4.2), (150.8, -2.6),
    (147.4, -1.95), (162.0, 5.32), (163.0, 5.3), (158.2, 6.9), (166.9, 9.4), (169.55, 6.03), (171.2, 7.1),
    (168.5, 7.1), (125.15, 1.45), (129.1, -1.1), (128.2, -3.7), (131.27, -0.85), (127.45, 1.3), (134.6, -1.3),
]

cf = json.load(open(NE + '/ne_10m_admin_0_countries.geojson'))
rings_by_unit = defaultdict(list)   # unit -> list of (ring, is_hole)
unmapped = set()
for f in cf['features']:
    a3 = f['properties']['ADM0_A3']
    unit = UNIT.get(a3, '?')
    g = f['geometry']
    for p in polys(g):
        for k, r in enumerate(p):
            pts = [shift(c) for c in r]
            b = bbox(pts)
            if b[2] < W or b[0] > E or b[3] < S or b[1] > N:
                continue
            if unit == '?':
                unmapped.add((a3, f['properties']['ADMIN']))
                continue
            if unit is None:
                continue
            u = unit
            if a3 == 'MYS':
                u = 'MAL' if b[0] < 105 else 'NBO'
            c = rnd(clip_ring(pts))
            if len(c) < 3:
                continue
            A = area(c)
            if abs(A) < MIN_AREA and k == 0:
                bx = bbox(c)
                if not any(bx[0] - .05 <= x <= bx[2] + .05 and bx[1] - .05 <= y <= bx[3] + .05 for x, y in KEY_ISLANDS):
                    continue
            # orientation: outer CCW (A>0), hole CW
            if (k == 0 and A < 0) or (k > 0 and A > 0):
                c = c[::-1]
            rings_by_unit[u].append(c)
print('unmapped', sorted(unmapped), file=sys.stderr)

# ---------------------------------------------------------------- union per unit (edge cancellation)
def union_rings(rings):
    edges = defaultdict(int)
    for r in rings:
        n = len(r)
        for i in range(n):
            a, b = r[i], r[(i + 1) % n]
            if a == b:
                continue
            if edges.get((b, a), 0) > 0:
                edges[(b, a)] -= 1
                if edges[(b, a)] == 0:
                    del edges[(b, a)]
            else:
                edges[(a, b)] += 1
    nxt = defaultdict(list)
    for (a, b), cnt in edges.items():
        for _ in range(cnt):
            nxt[a].append(b)
    out = []
    while nxt:
        start = next(iter(nxt))
        ring = [start]
        cur = start
        while True:
            lst = nxt.get(cur)
            if not lst:
                break
            b = lst.pop()
            if not lst:
                del nxt[cur]
            if b == start:
                break
            ring.append(b)
            cur = b
        if len(ring) >= 3:
            out.append(ring)
    return out

units = {}
for u, rs in rings_by_unit.items():
    units[u] = union_rings(rs)
    print(u, len(rs), '->', len(units[u]), file=sys.stderr)

# ---------------------------------------------------------------- shared arcs + topological simplification
owner = {}   # directed edge -> unit
for u, rs in units.items():
    for r in rs:
        n = len(r)
        for i in range(n):
            owner[(r[i], r[(i + 1) % n])] = u

def neighbour(u, a, b):
    return owner.get((b, a))

simplified = {}  # canonical arc key -> simplified points (in canonical direction)
borders = []     # (unitA, unitB, pts)
coasts = []      # pts
seen_border = set()

def canon(seq):
    t = tuple(seq)
    rv = tuple(reversed(seq))
    return (t, False) if t <= rv else (rv, True)

out_units = {}
for u, rs in units.items():
    out_rings = []
    for r in rs:
        n = len(r)
        nb = [neighbour(u, r[i], r[(i + 1) % n]) for i in range(n)]
        # rotate so that ring starts at a neighbour change (if any)
        start = 0
        for i in range(n):
            if nb[i] != nb[i - 1]:
                start = i
                break
        else:
            start = None
        if start is None:
            # whole ring has one neighbour (island or fully enclosed)
            pts = r + [r[0]]
            sp = dp(pts, TOL)
            if len(sp) < 4:
                sp = pts if len(pts) <= 8 else [pts[int(i * (len(pts) - 1) / 6)] for i in range(7)]
            ring = sp[:-1]
            if nb[0] is None:
                coasts.append(sp)
            else:
                key = canon(r)  # unlikely case: enclave
            out_rings.append(ring)
            continue
        rr = r[start:] + r[:start]
        nn = nb[start:] + nb[:start]
        runs = []
        i = 0
        while i < n:
            j = i
            while j + 1 < n and nn[j + 1] == nn[i]:
                j += 1
            seq = rr[i:j + 2] if j + 1 < n else rr[i:] + [rr[0]]
            runs.append((nn[i], seq))
            i = j + 1
        ring = []
        for v, seq in runs:
            key, rev = canon(seq)
            if key not in simplified:
                simplified[key] = dp(list(key), TOL)
                if v is None:
                    coasts.append(simplified[key])
                else:
                    pair = tuple(sorted((u, v)))
                    borders.append((u, v, simplified[key]))
            sp = simplified[key]
            if rev:
                sp = sp[::-1]
            ring.extend(sp[:-1])
        if len(ring) >= 3:
            out_rings.append(ring)
    out_units[u] = out_rings

nv = sum(len(r) for rs in out_units.values() for r in rs)
print('unit vertices', nv, 'border arcs', len(borders), 'coast arcs', len(coasts), file=sys.stderr)

# ---------------------------------------------------------------- Chinese provinces (internal borders + labels)
PROV = {
    'Beijing': 'HEB', 'Tianjin': 'HEB', 'Hebei': 'HEB', 'Shanghai': 'JSU', 'Jiangsu': 'JSU', 'Chongqing': 'SCH',
    'Sichuan': 'SCH', 'Hainan': 'GDG', 'Guangdong': 'GDG',
}
PNAMES = {
    'HEB': ['河北', 'Hebei', 115.3, 38.4], 'JSU': ['江苏', 'Jiangsu', 119.3, 33.0], 'SCH': ['四川', 'Sichuan', 104.5, 30.2],
    'GDG': ['广东', 'Guangdong', 113.4, 23.6], 'Shanxi': ['山西', 'Shanxi', 112.3, 37.4], 'Shaanxi': ['陕西', 'Shaanxi', 108.9, 35.3],
    'Shandong': ['山东', 'Shandong', 118.2, 36.3], 'Henan': ['河南', 'Henan', 113.6, 33.9], 'Hubei': ['湖北', 'Hubei', 112.3, 30.9],
    'Hunan': ['湖南', 'Hunan', 111.7, 27.6], 'Jiangxi': ['江西', 'Jiangxi', 115.7, 27.4], 'Anhui': ['安徽', 'Anhui', 117.2, 31.8],
    'Zhejiang': ['浙江', 'Zhejiang', 120.1, 29.2], 'Fujian': ['福建', 'Fujian', 118.1, 26.1], 'Guangxi': ['广西', 'Guangxi', 108.7, 23.8],
    'Guizhou': ['贵州', 'Guizhou', 106.8, 26.8], 'Yunnan': ['云南', 'Yunnan', 101.6, 24.6], 'Gansu': ['甘肃', 'Gansu', 103.8, 36.0],
    'Qinghai': ['青海', 'Qinghai', 96.5, 35.6], 'Ningxia': ['宁夏', 'Ningxia', 106.2, 37.5], 'Xinjiang': ['新疆', 'Xinjiang', 85.5, 41.5],
    'Xizang': ['西藏', 'Tibet', 88.5, 31.5], 'Liaoning': ['奉天', 'Fengtian', 122.6, 41.5], 'Jilin': ['吉林', 'Jilin', 126.5, 43.6],
    'Heilongjiang': ['黑龙江', 'Heilongjiang', 127.5, 47.6], 'Nei Mongol': None,
}
EXTRA_PLABELS = [['热河', 'Rehe', 118.4, 41.6], ['察哈尔', 'Chahar', 115.0, 42.3], ['绥远', 'Suiyuan', 110.4, 41.0],
                 ['西康', 'Xikang', 100.6, 30.8], ['兴安', 'Hsingan', 121.0, 47.0]]
a1 = json.load(open(NE + '/ne_10m_admin_1_states_provinces.geojson'))
prings = []
pnames_seen = set()
for f in a1['features']:
    pr = f['properties']
    if pr.get('adm0_a3') != 'CHN':
        continue
    nm = pr.get('name')
    pnames_seen.add(nm)
    gid = PROV.get(nm, nm)
    for p in polys(f['geometry']):
        r = rnd([tuple(c[:2]) for c in p[0]])
        if len(r) < 3:
            continue
        if area(r) < 0:
            r = r[::-1]
        prings.append((gid, r))
print('provinces', sorted(pnames_seen), file=sys.stderr)
pown = {}
for gid, r in prings:
    n = len(r)
    for i in range(n):
        pown[(r[i], r[(i + 1) % n])] = gid
plines_raw = []
used = set()
for gid, r in prings:
    n = len(r)
    i = 0
    cur = []
    for i in range(n + 1):
        a, b = r[i % n], r[(i + 1) % n]
        other = pown.get((b, a))
        internal = other is not None and other != gid and gid < other
        if internal:
            if not cur:
                cur = [a]
            cur.append(b)
        else:
            if len(cur) >= 2:
                plines_raw.append(cur)
            cur = []
    if len(cur) >= 2:
        plines_raw.append(cur)
plines = [dp(l, TOL * 1.6) for l in plines_raw]
plabels = []
for k, v in PNAMES.items():
    if v:
        plabels.append(v)
plabels += EXTRA_PLABELS

# ---------------------------------------------------------------- rivers / lakes
RIV = {'Yangtze', 'Chang Jiang', 'Huang', 'Huang He', 'Yellow', 'Xi', 'Xi Jiang', 'Huai', 'Han', 'Han Shui', 'Mekong',
       'Irrawaddy', 'Salween', 'Nu', 'Chindwin', 'Amur', 'Songhua', 'Songhua Jiang', 'Liao', 'Liao He', 'Yalu', 'Red',
       'Hong', 'Brahmaputra', 'Ganges', 'Ussuri', 'Nen', 'Nen Jiang', 'Xiang', 'Xiang Jiang', 'Gan', 'Gan Jiang', 'Wei',
       'Wei He', 'Fen', 'Fen He', 'Jialing', 'Min', 'Yuan', 'Lancang', 'Jinsha', 'Argun', 'Sittang', 'Fly', 'Sepik',
       'Murray', 'Darling', 'Mahakam', 'Kapuas', 'Barito', 'Chao Phraya', 'Ping', 'Nan', 'Hai', 'Yongding', 'Zi', 'Li',
       'Black', 'Da', 'Indus', 'Yamuna', 'Zeya', 'Bureya', 'Selenga', 'Kherlen', 'Onon', 'Lena', 'Yenisey', 'Angara',
       'Ob', 'Irtysh', 'Kolyma', 'Tumen', 'Taedong', 'Han-gang', 'Naktong', 'Shinano', 'Tone', 'Ishikari', 'Cagayan',
       'Pasig', 'Agusan', 'Mindanao', 'Musi', 'Batang Hari', 'Pahang', 'Perak', 'Rajang', 'Kinabatangan', 'Digul', 'Mamberamo'}
riv = json.load(open(NE + '/ne_10m_rivers_lake_centerlines.geojson'))
rivers = []
rnames = set()
for f in riv['features']:
    pr = f['properties']
    nm = pr.get('name') or ''
    sr = pr.get('scalerank', 10)
    if not (nm in RIV or sr <= 3):
        continue
    g = f['geometry']
    lines = g['coordinates'] if g['type'] == 'MultiLineString' else [g['coordinates']]
    for ln in lines:
        seg = [shift(c) for c in ln]
        seg = [p for p in seg if W <= p[0] <= E and S <= p[1] <= N]
        seg = rnd(dp(seg, 0.012), 3)
        if len(seg) >= 2:
            rivers.append({'n': nm, 'r': sr, 'l': seg})
            rnames.add(nm)
lk = json.load(open(NE + '/ne_10m_lakes.geojson'))
lakes = []
for f in lk['features']:
    pr = f['properties']
    if (pr.get('scalerank') or 10) > 5:
        continue
    for p in polys(f['geometry']):
        r = [shift(c) for c in p[0]]
        b = bbox(r)
        if b[2] < W or b[0] > E or b[3] < S or b[1] > N:
            continue
        r = rnd(dp(rnd(clip_ring(r)), 0.006), 3)
        if len(r) >= 3 and abs(area(r)) > 0.01:
            lakes.append(r)
print('rivers', len(rivers), 'lakes', len(lakes), file=sys.stderr)

# ---------------------------------------------------------------- Manchukuo outline from the 1938 basemap
hb = json.load(open(HB))
manchu = None
for f in hb['features']:
    if f['properties'].get('NAME') == 'Empire of Japan':
        for p in polys(f['geometry']):
            if len(p[0]) > 800:
                manchu = rnd(dp([tuple(c[:2]) for c in p[0]], 0.02), 3)

# ---------------------------------------------------------------- seeds
def spacing(u, x, y):
    if u == 'CHN':
        if x < 98:
            return 1.25
        if x < 103 or y > 45:
            return 0.8
        return 0.5
    if u == 'SUN':
        return 0.75 if (x > 115 and y < 54 and x < 142) else 1.7
    if u == 'MNG':
        return 1.0 if x > 110 else 1.5
    if u == 'IND':
        return 0.6 if x > 89 else 1.3
    if u == 'AUS':
        return 0.9 if y > -20 else 1.8
    if u in ('KOR', 'TWN', 'JPN', 'PHL', 'SLB', 'HKG', 'MAC'):
        return 0.42
    if u == 'USA':
        return 0.45 if (x > 195 and y < 30) else 1.2
    if u in ('NZL', 'AFG', 'IRN'):
        return 1.5
    return 0.55

ARCHIP = {'KIR', 'MHL', 'FSM', 'PLW', 'MNP', 'UMI', 'NRU', 'GUM', 'MAC', 'HKG', 'SLB', 'VUT', 'FJI', 'NCL'}
seeds = {}
for u, rs in out_units.items():
    pts = []
    outer = [r for r in rs if area(r) > 0]
    holes = [r for r in rs if area(r) < 0]
    for r in outer:
        bx = bbox(r)
        s0 = spacing(u, (bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2)
        A = area(r)
        own = []
        if A > 0.35 * s0 * s0:
            y = bx[1] + s0 * 0.43
            row = 0
            while y < bx[3]:
                s = spacing(u, (bx[0] + bx[2]) / 2, y)
                x = bx[0] + (s * 0.5 if row % 2 else 0) + s * 0.25
                while x < bx[2]:
                    s = spacing(u, x, y)
                    jx = x + (random.random() - .5) * s * .45
                    jy = y + (random.random() - .5) * s * .45
                    if pip(jx, jy, r) and not any(pip(jx, jy, h) for h in holes):
                        own.append((jx, jy))
                    x += s
                y += spacing(u, (bx[0] + bx[2]) / 2, y) * 0.866
                row += 1
        if not own:
            keyed = [(x, y) for x, y in KEY_ISLANDS if bx[0] - .02 <= x <= bx[2] + .02 and bx[1] - .02 <= y <= bx[3] + .02]
            if A > 0.12 * s0 * s0 or keyed or u in ARCHIP or (u == 'SUN' and bx[0] > 141 and bx[3] < 51.2):
                # interior point: centroid if inside, else midpoint of the widest scanline
                cx = sum(p[0] for p in r) / len(r)
                cy = sum(p[1] for p in r) / len(r)
                if not pip(cx, cy, r):
                    yy = (bx[1] + bx[3]) / 2
                    xs = []
                    n = len(r)
                    for i in range(n):
                        (x1, y1), (x2, y2) = r[i], r[(i + 1) % n]
                        if (y1 > yy) != (y2 > yy):
                            xs.append(x1 + (yy - y1) * (x2 - x1) / (y2 - y1))
                    xs.sort()
                    if len(xs) >= 2:
                        cx, cy = (xs[0] + xs[1]) / 2, yy
                own.append((cx, cy))
        pts.extend(own)
    seeds[u] = [[round(x, 2), round(y, 2)] for x, y in pts]
print('seeds', {u: len(v) for u, v in seeds.items()}, sum(len(v) for v in seeds.values()), file=sys.stderr)

def enc(r, d=4):
    return [[round(x, d), round(y, d)] for x, y in r]

out = {
    'box': [W, S, E, N],
    'units': {u: {'n': NAMES[u], 'r': [enc(r) for r in rs]} for u, rs in out_units.items()},
    'borders': [[a, b, enc(p)] for a, b, p in borders],
    'plines': [enc(l, 3) for l in plines],
    'plabels': plabels,
    'rivers': rivers,
    'lakes': lakes,
    'manchukuo': manchu,
    'seeds': seeds,
}
s = json.dumps(out, separators=(',', ':'), ensure_ascii=False)
open(OUT, 'w').write(s)
print('bytes', len(s), file=sys.stderr)
