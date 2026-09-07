#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build hugoyew.github.io static site from Feishu markdown sources."""
import re, html, os

SITE = os.path.dirname(os.path.abspath(__file__))

# ---------- markdown -> html ----------
def inline(s):
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'`(.+?)`', r'<code>\1</code>', s)
    return s

def md_to_html(md_text):
    lines = md_text.split('\n')
    out, i = [], 0
    in_list = False
    while i < len(lines):
        line = lines[i].rstrip()
        # table
        if line.startswith('|') and i + 1 < len(lines) and re.match(r'^\|[\s:|-]+\|$', lines[i+1].strip()):
            head = [c.strip() for c in line.strip('|').split('|')]
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append([inline(c.strip()) for c in lines[i].strip().strip('|').split('|')])
                i += 1
            t = ['<table>']
            t.append('<tr>' + ''.join(f'<td><b>{h}</b></td>' for h in head) + '</tr>')
            for r in rows:
                t.append('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>')
            t.append('</table>')
            out.append('\n'.join(t))
            continue
        # headings
        m = re.match(r'^(#{1,4})\s+(.*)$', line)
        if m:
            if in_list: out.append('</ul>'); in_list = False
            lvl = len(m.group(1)) + 1  # shift: # -> h2, ## -> h3, ### -> h4, #### -> h4-item
            if lvl > 4: lvl = 4
            out.append(f'<h{lvl}>{inline(m.group(2))}</h{lvl}>')
            i += 1; continue
        # list item
        if re.match(r'^[-*]\s+', line):
            if not in_list: out.append('<ul>'); in_list = True
            out.append(f'<li>{inline(re.sub(r"^[-*]\s+", "", line))}</li>')
            i += 1; continue
        if in_list: out.append('</ul>'); in_list = False
        # quote
        if line.startswith('>'):
            out.append(f'<blockquote><p>{inline(line.lstrip("> "))}</p></blockquote>')
            i += 1; continue
        # hr
        if re.match(r'^---+\s*$', line):
            i += 1; continue
        # paragraph
        if line.strip():
            out.append(f'<p>{inline(line)}</p>')
        i += 1
    if in_list: out.append('</ul>')
    return '\n'.join(out)

# ---------- resume ----------
def load_resume():
    with open(os.path.join(SITE, 'resume.md'), encoding='utf-8') as f:
        text = f.read()
    parts = re.split(r'^## (一、简体中文|二、繁體中文|三、English)\s*$', text, flags=re.M)
    # parts: [pre, '一、简体中文', body, '二、繁體中文', body, '三、English', body]
    body = {}
    for k in range(1, len(parts), 2):
        body[parts[k]] = parts[k+1].strip()
    # head info table
    head_m = re.search(r'## 头部信息\n(.*?)(?=\n## )', text, flags=re.S)
    head_rows = {}
    if head_m:
        for r in re.findall(r'\|([^|]+)\|([^|]+)\|', head_m.group(1)):
            head_rows[r[0].strip()] = r[1].strip()
    return body, head_rows

# ---------- page template ----------
def page(title, main_html, nav_active='', lang_switch=False, desc=''):
    lang_block = ''
    if lang_switch:
        lang_block = '''<div class="lang-switch" id="lang-switch">
  <button data-lang="zh" class="active">简</button>
  <button data-lang="tw">繁</button>
  <button data-lang="en">EN</button>
</div>'''
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="assets/style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🧑‍💻</text></svg>">
</head>
<body>
<nav><div class="nav-inner">
  <a class="brand" href="index.html">Hugo Yew</a>
  <div class="links">
    <a href="index.html" class="{'active' if nav_active=='home' else ''}">CV</a>
    <a href="track-record.html" class="{'active' if nav_active=='track' else ''}">Track Record</a>
    <a href="life.html" class="{'active' if nav_active=='life' else ''}">Life</a>
    {lang_block}
  </div>
</div></nav>
<main class="{'home' if nav_active=='home' else ''}">
{main_html}
</main>
<footer>
  <span>© {os.environ.get('BUILD_YEAR','2026')} Hugo Yew · 簡中 / 繁中 / English</span>
  <span><a href="research.html" style="color:var(--fg-secondary);text-decoration:none;">Research</a></span>
</footer>
</body>
</html>'''

# ---------- index ----------
def build_index(body, head):
    hero = f'''<div class="hero">
  <h1 id="hero-name-zh">姚颂文</h1>
  <p class="position" id="hero-pos-zh">{inline(body['一、简体中文'].split('\\n')[0].replace('**定位**：',''))}</p>
  <div class="meta" id="hero-meta-zh">
    <a href="mailto:{head.get('邮箱','')}">{head.get('邮箱','')}</a>
    &nbsp;·&nbsp; {head.get('电话','')} &nbsp;·&nbsp; {head.get('英文姓名','')}
  </div>
</div>'''
    def section_html(md_text):
        return md_to_html(md_text)
    sec_zh = section_html(body['一、简体中文'])
    sec_tw = section_html(body['二、繁體中文'])
    sec_en = section_html(body['三、English'])
    main = f'''{hero}
<section id="cv-zh" class="cv-lang">
  {sec_zh}
</section>
<section id="cv-tw" class="cv-lang" hidden>
  {sec_tw}
</section>
<section id="cv-en" class="cv-lang" hidden>
  {sec_en}
</section>
<script>
(function(){{
  var btns = document.querySelectorAll('#lang-switch button');
  var sects = {{ zh: document.getElementById('cv-zh'), tw: document.getElementById('cv-tw'), en: document.getElementById('cv-en') }};
  var heroName = {{ zh: '姚颂文', tw: '姚頌文', en: 'Chung Man Yew' }};
  var heroPos = {{}};
  function setLang(l){{
    for (var k in sects) sects[k].hidden = (k !== l);
    var hn = document.getElementById('hero-name-zh');
    var n = document.getElementById('hero-name');
    hn.textContent = heroName[l];
    btns.forEach(function(b){{ b.classList.toggle('active', b.dataset.lang === l); }});
  }}
  btns.forEach(function(b){{ b.addEventListener('click', function(){{ setLang(b.dataset.lang); }}); }});
  setLang('zh');
}})();
</script>'''
    return page('姚颂文 Hugo Yew — CV', main, 'home', lang_switch=True, desc='Hugo Yew — Investment Banking Analyst at CITIC CLSA')

# ---------- track record ----------
def build_track():
    ib = [('新乳业', 'newhope.png', '（待补充）')]
    pf = [('宁德时代 CATL · 港股', 'catl.png', '（待补充）'),
          ('Yarbo', 'yarbo.png', '（待补充）'),
          ('蜜雪冰城 · 港股', 'mixue-text.png', '（待补充）'),
          ('古茗 · 港股', 'guming.png', '（待补充）')]
    def wall(items):
        cards = ''
        for name, img, note in items:
            cards += f'''<div class="logo-card">
  <img src="assets/logos/{img}" alt="{name}">
  <div class="co">{name}</div>
  <div class="note">{note}</div>
</div>'''
        return f'<div class="logo-wall">{cards}</div>'
    main = f'''<h1 style="font-size:40px;font-weight:700;letter-spacing:-0.022em;margin-bottom:12px;">Track Record</h1>
<p style="color:var(--fg-secondary);margin-bottom:44px;font-size:16px;">Selected deals & investments</p>

<section>
  <h2>Investment Banking</h2>
  {wall(ib)}
</section>
<section>
  <h2>Investments</h2>
  {wall(pf)}
</section>'''
    return page('Track Record — Hugo Yew', main, 'track', desc='Selected deals and investments')

# ---------- research ----------
DEEP = [('消费零售 · 万店连锁与识别框架', 'https://my.feishu.cn/docx/ADwvd0PL6oxkTVxp1gwcKmoinAh'),
        ('阔手机 · Phase 1 研究', 'https://my.feishu.cn/docx/CiJadMTc4oX0F2x9vc8cTHbSnaf'),
        ('新风天域 · 估值案例复盘', 'https://my.feishu.cn/docx/MzQPd5KNHoLpmDxYUaIcm0Lunlb'),
        ('TOPTOY · Masterdoc', 'https://my.feishu.cn/docx/ZQcgdQwkMooSHLxZEjWc8ufTnEF'),
        ('POPMART 泡泡玛特 · Masterdoc', 'https://my.feishu.cn/docx/IHdldp1W6oN2ATxizXAcSd8FnCK')]
FRAME = [('Consumer 消费框架', 'https://my.feishu.cn/docx/JeQKdHqslollZbxRSxycd23Fnze'),
         ('Healthcare 医疗框架', 'https://my.feishu.cn/docx/WxtLdFaDAo8WQGxHcBjcZOTAnFj'),
         ('TMT 框架', 'https://my.feishu.cn/docx/Oj5WdUI2gofZiex5Zrtcw0VLnPe'),
         ('Industrial 工业框架', 'https://my.feishu.cn/docx/COPOdwygBoSNWaxB6W3cBMtcnwg'),
         ('Financial 金融框架', 'https://my.feishu.cn/docx/U7aMdqEuFod0SCx4P1pcHrj2nxe')]

def build_research():
    def group(title, items):
        lis = ''
        for name, url in items:
            lis += f'''<a class="research-item" href="{url}" target="_blank" rel="noopener">
  <div class="rt">{name}</div>
  <div class="rd">View on Feishu →</div>
</a>'''
        return f'<section><h2>{title}</h2>{lis}</section>'
    main = f'''<h1 style="font-size:40px;font-weight:700;letter-spacing:-0.022em;margin-bottom:12px;">Research</h1>
<p style="color:var(--fg-secondary);margin-bottom:44px;font-size:16px;">Equity research & industry frameworks.<br>By invitation only — please do not share or index.</p>
{group('Deep Dives', DEEP)}
{group('Industry Frameworks', FRAME)}'''
    return page('Research — Hugo Yew', main, desc='Equity research by Hugo Yew (by invitation)')

# ---------- life ----------
def build_life():
    main = '''<div class="life-placeholder">
  <div style="font-size:40px;margin-bottom:16px;">🌱</div>
  Life beyond the desk<br>
  <span style="font-size:14px;">Coming soon</span>
</div>'''
    return page('Life — Hugo Yew', main, 'life', desc='Life beyond the desk')

# ---------- robots ----------
def build_robots():
    return 'User-agent: *\nDisallow: /research.html\n'

if __name__ == '__main__':
    body, head = load_resume()
    with open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(build_index(body, head))
    with open(os.path.join(SITE, 'track-record.html'), 'w', encoding='utf-8') as f:
        f.write(build_track())
    with open(os.path.join(SITE, 'research.html'), 'w', encoding='utf-8') as f:
        f.write(build_research())
    with open(os.path.join(SITE, 'life.html'), 'w', encoding='utf-8') as f:
        f.write(build_life())
    with open(os.path.join(SITE, 'robots.txt'), 'w', encoding='utf-8') as f:
        f.write(build_robots())
    print('built:', os.listdir(SITE))
