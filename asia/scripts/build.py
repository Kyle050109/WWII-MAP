"""Assemble asia/index.html from src/ and data/.  usage: python3 scripts/build.py [--artifact]"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
HEAD = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="第二次世界大战亚洲及太平洋战场互动地图（1937–1945）：省份网格、逐日战线、攻势箭头与重大事件，中英双语。">
<style>body{margin:0}[hidden]{display:none!important}:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}</style>
"""
def main():
    t = (ROOT / 'src/template.html').read_text(encoding='utf-8')
    t = t.replace('/*__GEO__*/', 'window.PAGEO=' + (ROOT / 'data/asia_geo.json').read_text(encoding='utf-8') + ';')
    t = t.replace('/*__CONTROL__*/', (ROOT / 'src/control.js').read_text(encoding='utf-8'))
    t = t.replace('/*__STORY__*/', (ROOT / 'src/story.js').read_text(encoding='utf-8'))
    if '--artifact' in sys.argv:
        out = ROOT / 'build/pacific-ablaze.html'
        out.parent.mkdir(exist_ok=True)
        out.write_text(t, encoding='utf-8')
    else:
        t = t.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
        split = t.index('<div id="app">')
        page = HEAD + t[:split] + '</head>\n<body>\n' + t[split:] + '\n</body>\n</html>\n'
        out = ROOT / 'index.html'
        out.write_text(page, encoding='utf-8')
    print(out, out.stat().st_size // 1024, 'KB')
if __name__ == '__main__':
    main()
