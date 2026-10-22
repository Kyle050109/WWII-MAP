"""Assemble index.html from src/ and data/.

Usage: python3 scripts/build.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HEAD = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<meta name="description" content="二战欧洲战场互动地图（1939–1945）：时间轴、战线变化、攻势箭头与重大事件，中英双语。">
<style>body{margin:0}[hidden]{display:none!important}:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}</style>
"""

def main():
    t = (ROOT / 'src/template.html').read_text(encoding='utf-8')
    t = t.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
    t = t.replace('/*__GEO__*/', 'window.WW2GEO=' + (ROOT / 'data/geo.json').read_text(encoding='utf-8') + ';')
    t = t.replace('/*__FRONTS__*/', (ROOT / 'src/fronts.js').read_text(encoding='utf-8'))
    t = t.replace('/*__EVENTS__*/', (ROOT / 'src/events.js').read_text(encoding='utf-8'))
    # the template's <title>, fonts and <style> belong in <head>; the rest in <body>
    split = t.index('<div id="app">')
    page = HEAD + t[:split] + '</head>\n<body>\n' + t[split:] + '\n</body>\n</html>\n'
    (ROOT / 'index.html').write_text(page, encoding='utf-8')
    print(f'index.html written ({len(page) // 1024} KB)')

if __name__ == '__main__':
    main()
