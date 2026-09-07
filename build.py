#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build hugoyew.github.io — dark one-pager, capability-driven CV, article-based research."""
import re, os, html

SITE = os.path.dirname(os.path.abspath(__file__))

# ============ markdown -> article html ============
def inline(s):
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'\$([^$]+)\$', r'<i>\1</i>', s)          # inline latex -> italic
    s = re.sub(r'\$\$(.+?)\$\$', r'<i>\1</i>', s, flags=re.S)
    s = re.sub(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', r'\1', s)  # obsidian wiki links
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    return s

def md_to_article(md_text):
    # strip feishu <title> line and obsidian YAML frontmatter block at the top
    m = re.match(r'^(?:<title>.*?</title>\s*)?---\n.*?\n---\s*\n', md_text, flags=re.S)
    if m:
        md_text = md_text[m.end():]
    lines = md_text.split('\n')
    out, i = [], 0
    in_list = False; in_ol = False; in_code = False
    while i < len(lines):
        line = lines[i].rstrip()
        # code fence
        if line.strip().startswith('```'):
            if not in_code:
                in_code = True; out.append('<pre><code>'); i += 1; continue
            else:
                in_code = False; out.append('</code></pre>'); i += 1; continue
        if in_code:
            out.append(html.escape(line)); i += 1; continue
        # table
        if line.startswith('|') and i + 1 < len(lines) and re.match(r'^\|[\s:|-]+\|$', lines[i+1].strip()):
            if in_list: out.append('</ul>'); in_list = False
            if in_ol: out.append('</ol>'); in_ol = False
            head = [c.strip() for c in line.strip('|').split('|')]
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append([inline(c.strip()) for c in lines[i].strip().strip('|').split('|')])
                i += 1
            t = ['<table>', '<thead><tr>'] + [f'<th>{h}</th>' for h in head] + ['</tr></thead><tbody>']
            for r in rows:
                t.append('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>')
            t.append('</tbody></table>')
            out.append('\n'.join(t)); continue
        # headings (skip h1 — article title is in page)
        m = re.match(r'^(#{2,6})\s+(.*)$', line)
        if m:
            if in_list: out.append('</ul>'); in_list = False
            if in_ol: out.append('</ol>'); in_ol = False
            lvl = min(len(m.group(1)), 4)
            out.append(f'<h{lvl}>{inline(m.group(2))}</h{lvl}>')
            i += 1; continue
        if re.match(r'^#\s+', line):
            i += 1; continue
        # bullets
        if re.match(r'^[-*]\s+', line):
            if in_ol: out.append('</ol>'); in_ol = False
            if not in_list: out.append('<ul>'); in_list = True
            out.append(f'<li>{inline(re.sub(r"^[-*]\s+", "", line))}</li>')
            i += 1; continue
        # numbered list
        m = re.match(r'^(\d+)[.、)]\s+(.*)$', line)
        if m:
            if in_list: out.append('</ul>'); in_list = False
            if not in_ol: out.append('<ol>'); in_ol = True
            out.append(f'<li>{inline(m.group(2))}</li>')
            i += 1; continue
        if in_list: out.append('</ul>'); in_list = False
        if in_ol: out.append('</ol>'); in_ol = False
        # quote / callout
        if line.startswith('>'):
            q = re.sub(r'^>\s*', '', line)
            q = re.sub(r'^\[!(?:important|note|warning|tip)\][\s-]*', '', q)
            out.append(f'<blockquote><p>{inline(q)}</p></blockquote>')
            i += 1; continue
        # hr
        if re.match(r'^---+\s*$', line) or re.match(r'^___+$', line):
            if in_list: out.append('</ul>'); in_list = False
            out.append('<hr>'); i += 1; continue
        # paragraph
        if line.strip():
            out.append(f'<p>{inline(line)}</p>')
        i += 1
    if in_list: out.append('</ul>')
    if in_ol: out.append('</ol>')
    return '\n'.join(out)

# ============ research metadata ============
RESEARCH = {
    'popmart':   dict(title='POP MART Masterdoc', cat='consumer', no='01',
                      logo='popmart.png', cover='',
                      desc='IP 投资引擎 × 全球化零售渠道：从效率三角到造星机制的完整拆解。'),
    'wandian':   dict(title='万店连锁 × 识别框架', cat='consumer', no='02',
                      logo='', cover='coffee.jpg',
                      desc='从蜜雪到瑞幸：万店连锁背后的渠道、供应链与心智三层识别框架。'),
    'kuoshouji': dict(title='阔手机 Phase 1 研究', cat='consumer', no='03',
                      logo='', cover='kuoshouji.jpg',
                      desc='折叠屏 → 阔手机：品类迁移的早期判断与跟踪。'),
    'newfrontier': dict(title='新风天域 · 估值案例复盘', cat='healthcare', no='04',
                        logo='nf.png', cover='',
                        desc='从一次真实的港股 IPO 估值过会，提炼可复用的估值逻辑链与叙事手法。'),
}
CATS = [
    ('consumer', '消费 & 零售', 'Consumer & Retail'),
    ('healthcare', '医疗健康', 'Healthcare'),
]
SLUG_TITLES = {'popmart':'POP MART Masterdoc','wandian':'万店连锁识别框架',
               'kuoshouji':'阔手机 Phase 1','newfrontier':'新风天域估值案例'}

# ============ page shell ============
def shell(title, body, desc='', lang_switch=False):
    ls = '''<div class="lang-switch" id="lang-switch"><button data-lang="zh" class="active">简</button><button data-lang="tw">繁</button><button data-lang="en">EN</button></div>''' if lang_switch else ''
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<nav><div class="nav-inner">
  <a class="nav-brand" href="../index.html">Hugo Yew</a>
  <div class="nav-links">
    <a href="../index.html">CV</a>
    <a href="../index.html#track">Track Record</a>
    <a href="../index.html#research">Research</a>
    <a href="../index.html#life">Life</a>
    {ls}
  </div>
</div></nav>
{body}
</body>
</html>'''

def index_shell(title, body, desc=''):
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
{body}
</body>
</html>'''

# ============ capability CV (trilingual) ============
CAPS = {
'zh': [
  ('01', '港股 IPO 执行',
   '从行业格局与竞争壁垒研究，到招股书章节起草与可比公司估值，覆盖 IPO 全流程的关键环节。',
   ['中信里昂证券 CLSA · 投行部分析师（2026.06 – 至今）',
    '参与多家拟港股上市企业的 IPO 执行，覆盖医疗健康、科技与消费',
    '为 A 股上市公司 H 股上市补充材料提供估值与报告支持']),
  ('02', '跨境并购与财务顾问',
   '卖方项目从投资故事到交易执行：估值、买家分析与英文提案。',
   ['东南亚跨境医疗健康机构少数股权出售 · FA 项目',
    'Trading Comps / Transaction Comps 估值与战略买家分析',
    '英文 RFP 提案制作']),
  ('03', '消费行业深度研究',
   '以投资视角拆解消费公司与行业：从 Pre-IPO 尽调到潮玩、现制茶饮、出海。',
   ['元生资本 · 消费投资（货拉拉 / 东鹏特饮 / 宁德时代 Pre-IPO 尽调）',
    '源一资本 · 港股新消费（老铺黄金 / 泡泡玛特 / 布鲁可 / 名创优品）',
    '潮玩行业 50+ 页深度报告 · 300 份消费者问卷',
    '研报：<a href="research/popmart.html">POP MART</a>  · <a href="research/wandian.html">万店连锁</a> · <a href="research/kuoshouji.html">阔手机</a>']),
  ('04', '估值建模与投研叙事',
   '把复杂公司讲成清晰投资故事：建模、对标与案例复盘。',
   ['HollySys LBO 分析 · 投资银行课程',
    '<a href="research/newfrontier.html">新风天域估值案例复盘</a>（港股 IPO 过会级）',
    '跨消费零售与医疗健康的深度研究体系']),
],
'tw': [
  ('01', '港股 IPO 執行',
   '從行業格局與競爭壁壘研究，到招股書章節起草與可比公司估值，覆蓋 IPO 全流程的關鍵環節。',
   ['中信里昂證券 CLSA · 投行部分析師（2026.06 – 至今）',
    '參與多家擬港股上市企業的 IPO 執行，覆蓋醫療健康、科技與消費',
    '為 A 股上市公司 H 股上市補充材料提供估值與報告支持']),
  ('02', '跨境併購與財務顧問',
   '賣方項目從投資故事到交易執行：估值、買家分析與英文提案。',
   ['東南亞跨境醫療健康機構少數股權出售 · FA 項目',
    'Trading Comps / Transaction Comps 估值與戰略買家分析',
    '英文 RFP 提案製作']),
  ('03', '消費行業深度研究',
   '以投資視角拆解消費公司與行業：從 Pre-IPO 盡調到潮玩、現製茶飲、出海。',
   ['元生資本 · 消費投資（貨拉拉 / 東鵬特飲 / 寧德時代 Pre-IPO 盡調）',
    '源壹資本 · 港股新消費（老鋪黃金 / 泡泡瑪特 / 布魯可 / 名創優品）',
    '潮玩行業 50+ 頁深度報告 · 300 份消費者問卷',
    '研報：<a href="research/popmart.html">POP MART</a>  · <a href="research/wandian.html">萬店連鎖</a> · <a href="research/kuoshouji.html">闊手機</a>']),
  ('04', '估值建模與投研敘事',
   '把複雜公司講成清晰投資故事：建模、對標與案例復盤。',
   ['HollySys LBO 分析 · 投資銀行課程',
    '<a href="research/newfrontier.html">新風天域估值案例復盤</a>（港股 IPO 過會級）',
    '跨消費零售與醫療健康的深度研究體系']),
],
'en': [
  ('01', 'Hong Kong IPO Execution',
   'From industry landscape and competitive moat research to prospectus drafting and comparable valuation — across the critical stages of an IPO.',
   ['Analyst, Investment Banking at CLSA (Jun 2026 – Present)',
    'IPO execution for multiple Hong Kong-bound companies across healthcare, TMT and consumer',
    'Valuation and report support for an A-share issuer\u2019s H-share listing']),
  ('02', 'Cross-border M&A Advisory',
   'Sell-side mandates from investment story to execution: valuation, buyer analysis and English proposals.',
   ['Sell-side FA on a minority stake disposal in a Southeast Asian healthcare institution',
    'Trading Comps & Transaction Comps, strategic and financial buyer analysis',
    'English RFP pitch book']),
  ('03', 'Consumer Sector Research',
   'Deconstructing consumer companies through an investment lens — from Pre-IPO due diligence to collectibles, tea chains and going-global.',
   ['Genesis Capital · Consumer Investing (Lalamove / Eastroc / CATL Pre-IPO CDD)',
    'Being Capital · HK-listed new consumer (LAOPU / POPMART / Bloks / MINISO)',
    '50+ page collectibles deep-dive · 300 consumer surveys',
    'Reports: <a href="research/popmart.html">POP MART</a>  · <a href="research/wandian.html">Wan-dian chains</a> · <a href="research/kuoshouji.html">Wide phones</a>']),
  ('04', 'Valuation & Investment Narrative',
   'Turning complex companies into clear stories: modeling, benchmarking and case teardowns.',
   ['HollySys LBO analysis · Investment Banking coursework',
    '<a href="research/newfrontier.html">New Frontier valuation teardown</a> (HK IPO pass-level)',
    'A deep research system across consumer & retail and healthcare']),
],
}
HERO = {
'zh': dict(kicker='INVESTMENT BANKING · CONSUMER RESEARCH · VENTURE',
           name='姚颂文', name2='Hugo Yew',
           pos='横跨投行与 VC 的分析师——参与港股 IPO 执行、跨境并购与消费投资研究，用深度研究驱动每一笔判断。',
           meta='hugoyewtt@gmail.com · (+86) 134-5005-0927 · (+852) 6956-9276'),
'tw': dict(kicker='INVESTMENT BANKING · CONSUMER RESEARCH · VENTURE',
           name='姚頌文', name2='Hugo Yew',
           pos='橫跨投行與 VC 的分析師——參與港股 IPO 執行、跨境併購與消費投資研究，用深度研究驅動每一筆判斷。',
           meta='hugoyewtt@gmail.com · (+86) 134-5005-0927 · (+852) 6956-9276'),
'en': dict(kicker='INVESTMENT BANKING · CONSUMER RESEARCH · VENTURE',
           name='Chung Man Yew', name2='Hugo Yew',
           pos='Analyst spanning investment banking and venture capital — IPO execution, cross-border M&A and consumer investing, driven by deep research.',
           meta='hugoyewtt@gmail.com · (+86) 134-5005-0927 · (+852) 6956-9276'),
}
TIMELINE = {
'zh': [
  ('中信里昂证券 CLSA', '投资银行部分析师', '2026.06 – 至今', ['港股 IPO 执行与跨境并购财务顾问']),
  ('元生资本', '消费投资实习生', '2025.02 – 2025.09', ['Pre-IPO 投资研究 · 3 起港股 IPO 尽调']),
  ('源一资本', '消费投资实习生', '2024.09 – 2025.02', ['港股新消费深度研究 · 潮玩行业独立研究']),
  ('复旦大学 国际金融学院', '金融学硕士', '2024.09 – 2026.06', ['FISF']),
  ('中山大学 岭南学院', '国际商务学士', '2020.09 – 2024.06', ['康乐杯篮球赛冠军队长']),
],
'tw': [
  ('中信里昂證券 CLSA', '投資銀行部分析師', '2026.06 – 至今', ['港股 IPO 執行與跨境併購財務顧問']),
  ('元生資本', '消費投資實習生', '2025.02 – 2025.09', ['Pre-IPO 投資研究 · 3 起港股 IPO 盡調']),
  ('源壹資本', '消費投資實習生', '2024.09 – 2025.02', ['港股新消費深度研究 · 潮玩行業獨立研究']),
  ('復旦大學 國際金融學院', '金融學碩士', '2024.09 – 2026.06', ['FISF']),
  ('中山大學 嶺南學院', '國際商務學士', '2020.09 – 2024.06', ['康樂杯籃球賽冠軍隊長']),
],
'en': [
  ('CITIC CLSA', 'Analyst, Investment Banking', 'Jun 2026 – Present', ['HK IPO execution & cross-border M&A advisory']),
  ('Genesis Capital', 'Consumer Investment Intern', 'Feb 2025 – Sep 2025', ['Pre-IPO research · CDD on 3 HK IPO deals']),
  ('Being Capital', 'Consumer Investment Intern', 'Sep 2024 – Feb 2025', ['HK new-consumer deep research · collectibles']),
  ('Fudan University · FISF', 'MSc Finance', 'Sep 2024 – Jun 2026', ['']),
  ('Sun Yat-sen University · Lingnan', 'BSc International Business', 'Sep 2020 – Jun 2024', ['Champion basketball captain']),
],
}

def life_photos(items):
    return '<div class="life-photos">' + ''.join(
        f'<div class="life-item"><div class="life-photo"><img src="assets/photos/{img}" alt="{alt}"></div><div class="cap">{cap}</div></div>'
        for img, alt, cap in items) + '</div>'

def build_index():
    def caps_html(lang):
        cards = ''
        for num, title, desc, ev in CAPS[lang]:
            lis = ''.join(f'<li>{e}</li>' for e in ev)
            cards += f'''<div class="cap-card"><div class="cap-num">{num}</div><h3>{title}</h3><p>{desc}</p><ul class="cap-evidence">{lis}</ul></div>'''
        return f'<div class="caps">{cards}</div>'
    def timeline_html(lang):
        items = ''
        for org, role, date, pts in TIMELINE[lang]:
            right = ''.join(f'<li>{p}</li>' for p in pts) if pts else '<ul></ul>'
            items += f'''<div class="t-item"><div class="t-left"><div class="t-org">{org}</div><div class="t-role">{role}</div><div class="t-date">{date}</div></div><div class="t-right"><ul>{right}</ul></div></div>'''
        return f'<div class="timeline">{items}</div>'
    def logo_wall():
        ib = [('新乳业', 'newhope.png', 'IPO 执行', '')]
        pf = [('宁德时代 CATL', 'catl.png', '港股 · Pre-IPO 研究', ''),
              ('Yarbo', 'yarbo.png', '早期投资', ''),
              ('蜜雪冰城', 'mixue-text.png', '港股 · 研究', ''),
              ('古茗', 'guming.png', '港股 · 研究', ''),
              ('货拉拉 Lalamove', 'lalamove.png', '港股 · 研究', ''),
              ('Uwant 友望', 'uwant.png', '早期投资', '')]
        def wall(items):
            return '<div class="logo-wall">' + ''.join(
                f'<div class="logo-card"><img src="assets/logos/{img}" class="{cls}" alt="{n}"><div class="co">{n}</div><div class="note">{note}</div></div>'
                for n, img, note, cls in items) + '</div>'
        return f'''<div class="track-cols">
  <div class="track-col"><div class="group-label">Investment Banking</div>{wall(ib)}</div>
  <div class="track-col"><div class="group-label">Investments</div>{wall(pf)}</div>
</div>'''
    def research_grid():
        out = ''
        for cat_key, cat_zh, cat_en in CATS:
            cards = ''
            for slug, meta in RESEARCH.items():
                if meta['cat'] != cat_key: continue
                if meta['logo']:
                    cover = f'''<div class="r-cover r-logo"><img src="assets/logos/{meta['logo']}" alt="{meta['title']}"><div class="r-no">{meta['no']}</div><div class="r-cat">{cat_en}</div></div>'''
                elif meta.get('cover'):
                    cover = f'''<div class="r-cover r-img" style="background-image:url(assets/covers/{meta['cover']})"><div class="r-no">{meta['no']}</div><div class="r-cat">{cat_en}</div><div class="r-title">{meta['title']}</div></div>'''
                else:
                    cover = f'''<div class="r-cover g1"><div class="r-no">{meta['no']}</div><div class="r-cat">{cat_en}</div><div class="r-title">{meta['title']}</div></div>'''
                cards += f'''<a class="r-card" href="research/{slug}.html">
  {cover}
  <div class="r-body"><div class="r-title-sm">{meta['title']}</div><div class="r-desc">{meta['desc']}</div><div class="r-meta"><span>{SLUG_TITLES[slug]}</span><span>→</span></div></div>
</a>'''
            out += f'''<div class="r-category"><h3>{cat_zh} <span style="color:var(--fg-tertiary);font-weight:400;font-size:13px;">{cat_en}</span></h3><div class="r-grid">{cards}</div></div>'''
        return out
    def section(ids, tag, title, sub, inner):
        return f'''<div class="section" id="{ids}"><div class="section-tag">{tag}</div><h2 class="section-title">{title}</h2><p class="section-sub">{sub}</p>{inner}</div>'''
    def hero_block(lang):
        h = HERO[lang]
        return f'''<div class="hero"><div class="hero-wrap">
  <div class="hero-text">
    <div class="hero-kicker">{h['kicker']}</div>
    <h1>{h['name']}</h1>
    <p class="position">{h['pos']}</p>
    <div class="meta">{h['meta']}</div>
  </div>
  <div class="hero-photo"><img src="assets/photos/professional.jpg" alt="Hugo Yew"></div>
</div></div>'''
    hero_zh = hero_block('zh'); hero_tw = hero_block('tw'); hero_en = hero_block('en')
    # duplicate hero ids must be unique per language — use data-lang wrappers
    nav = '''<nav><div class="nav-inner">
  <a class="nav-brand" href="index.html">Hugo Yew</a>
  <div class="nav-links">
    <a href="#hero">Home</a>
    <a href="#capabilities">Capabilities</a>
    <a href="#track">Track Record</a>
    <a href="#research">Research</a>
    <a href="#life">Life</a>
    <div class="lang-switch" id="lang-switch"><button data-lang="zh" class="active">简</button><button data-lang="tw">繁</button><button data-lang="en">EN</button></div>
  </div>
</div></nav>'''
    body = f'''{nav}
<main>
  <div data-lang-block="zh">{hero_zh}</div>
  <div data-lang-block="tw" hidden>{hero_tw}</div>
  <div data-lang-block="en" hidden>{hero_en}</div>

  <div data-lang-block="zh">{section('capabilities','Capabilities','核心能力','先说我擅长什么，再用经历与作品证明。', caps_html('zh'))}</div>
  <div data-lang-block="tw" hidden>{section('capabilities','Capabilities','核心能力','先說我擅長什麼，再用經歷與作品證明。', caps_html('tw'))}</div>
  <div data-lang-block="en" hidden>{section('capabilities','Capabilities','Core Capabilities','What I do well — proven by work, not titles.', caps_html('en'))}</div>

  <div data-lang-block="zh">{section('track','Track Record','代表性项目','参与过的关键交易与投资。', logo_wall())}</div>
  <div data-lang-block="tw" hidden>{section('track','Track Record','代表性項目','參與過的關鍵交易與投資。', logo_wall())}</div>
  <div data-lang-block="en" hidden>{section('track','Track Record','Selected Work','Key deals and investments I have been part of.', logo_wall())}</div>

  <div data-lang-block="zh">{section('research','Research','研究','成体系的研究输出：消费零售、医疗健康与跨行业框架。', research_grid())}</div>
  <div data-lang-block="tw" hidden>{section('research','Research','研究','成體係的研究輸出：消費零售、醫療健康與跨行業框架。', research_grid())}</div>
  <div data-lang-block="en" hidden>{section('research','Research','Research','Systematic research output: consumer & retail, healthcare, and cross-industry frameworks.', research_grid())}</div>

  <div data-lang-block="zh">{section('life','Life','生活之外','工作之外的我。', life_photos([('gym.jpg','健身','健身'),('nyc.jpg','纽约','Biodesign Challenge 纽约决赛'),('coffee.jpg','手冲','手冲咖啡'),('referee.jpg','篮球裁判','国家二级篮球裁判'),('captain.jpg','篮球指挥','岭南队 3 号 · 队长')]))}</div>
  <div data-lang-block="tw" hidden>{section('life','Life','生活之外','工作之外的我。', life_photos([('gym.jpg','健身','健身'),('nyc.jpg','紐約','Biodesign Challenge 紐約決賽'),('coffee.jpg','手沖','手沖咖啡'),('referee.jpg','籃球裁判','國家二級籃球裁判'),('captain.jpg','籃球指揮','嶺南隊 3 號 · 隊長')]))}</div>
  <div data-lang-block="en" hidden>{section('life','Life','Beyond Work','Life outside the desk.', life_photos([('gym.jpg','Fitness','Fitness'),('nyc.jpg','New York','Biodesign Challenge · NYC finals'),('coffee.jpg','Coffee','Pour-over'),('referee.jpg','Basketball','National Level II referee'),('captain.jpg','Captain','Lingnan #3 · team captain')]))}</div>
</main>
<footer>
  <span>© 2026 Hugo Yew · 簡中 / 繁中 / English</span>

</footer>
<script>
(function(){{
  var btns = document.querySelectorAll('#lang-switch button');
  var blocks = document.querySelectorAll('[data-lang-block]');
  function setLang(l){{
    blocks.forEach(function(b){{ b.hidden = (b.getAttribute('data-lang-block') !== l); }});
    btns.forEach(function(b){{ b.classList.toggle('active', b.dataset.lang === l); }});
  }}
  btns.forEach(function(b){{ b.addEventListener('click', function(){{ setLang(b.dataset.lang); }}); }});
  setLang('zh');
}})();
</script>
</body></html>'''
    return index_shell('姚颂文 Hugo Yew', body, 'Hugo Yew — Investment Banking Analyst at CITIC CLSA')

# ============ research article pages ============
def parse_frontmatter(md_text):
    fm = {}
    m = re.match(r'^(?:<title>.*?</title>\s*)?---\n(.*?)\n---', md_text, flags=re.S)
    if m:
        lines = m.group(1).split('\n')
        i = 0
        while i < len(lines):
            ln = lines[i]
            stripped = ln.strip()
            if ':' in stripped and not stripped.startswith('-'):
                k, _, v = stripped.partition(':')
                key = k.strip().lower()
                val = v.strip()
                if val == '|':
                    block = []
                    i += 1
                    while i < len(lines) and (lines[i].startswith('  ') or lines[i].startswith('\t') or lines[i].strip() == ''):
                        if lines[i].strip():
                            block.append(lines[i].strip())
                        i += 1
                    fm[key] = '\n'.join(block)
                    continue
                else:
                    fm[key] = val.strip('"').strip('\'')
            i += 1
    return fm

def section_after(md_text, keywords):
    """Return the first matching section (heading + content until next heading)."""
    lines = md_text.split('\n')
    for i, ln in enumerate(lines):
        if re.match(r'^#{1,4}\s+', ln) and re.sub(r'^#{1,4}\s+', '', ln).strip().lower() in keywords:
            body = []
            for j in range(i + 1, len(lines)):
                if re.match(r'^#{1,4}\s+', lines[j]):
                    break
                if lines[j].strip():
                    body.append(lines[j].strip())
            if body:
                return md_to_article('\n'.join(body))
    return ''

def build_articles():
    for slug, meta in RESEARCH.items():
        src = os.path.join(SITE, 'research_raw', f'{slug}.md')
        if not os.path.exists(src):
            continue
        with open(src, encoding='utf-8') as f:
            md = f.read()
        fm = parse_frontmatter(md)
        content = md_to_article(md)
        cat_en = dict((k, en) for k, zh, en in CATS)[meta['cat']]

        # executive summary: frontmatter summary -> explicit section -> meta desc
        summary = fm.get('summary', '')
        if not summary:
            summary = section_after(md, ['执行摘要', 'executive summary', '摘要', 'summary'])
        if not summary:
            summary = f'<p>{meta["desc"]}</p>'

        # conclusion: explicit section or placeholder
        conclusion = section_after(md, ['总结', '结论', '结语', 'conclusion', '结论与展望', '核心结论'])
        if not conclusion:
            conclusion = '<p class="muted">结论部分整理中——后续将按统一模板补齐。</p>'

        # extra meta chips from frontmatter
        chips = []
        if fm.get('ticker'): chips.append(f'<span class="chip">{html.escape(fm["ticker"])}</span>')
        if fm.get('last_updated') or fm.get('updated'): chips.append(f'<span class="chip">更新 {html.escape(fm.get("last_updated") or fm.get("updated"))}</span>')
        chips_html = '<div class="a-chips">' + ''.join(chips) + '</div>' if chips else ''

        if meta['logo']:
            hero_media = f'<img class="a-logo" src="../assets/logos/{meta["logo"]}" alt="">'
        elif meta.get('cover'):
            hero_media = f'<div class="a-cover" style="background-image:url(../assets/covers/{meta["cover"]})"></div>'
        else:
            hero_media = ''
        body = f'''<div class="article-hero">
  {hero_media}
  <div class="a-hd">
    <div class="r-cat">{cat_en} · {meta['no']}</div>
    <h1>{meta['title']}</h1>
    <div class="a-meta">{meta['desc']}</div>
    {chips_html}
  </div>
</div>
<div class="article">
  <div class="exec-summary"><h2>执行摘要 · Executive Summary</h2>{summary}</div>
  <div class="a-body">
{content}
  </div>
  <div class="conclusion"><h2>总结 · Conclusion</h2>{conclusion}</div>
  <div class="financials">
    <h2>财务数据 · Financials</h2>
    <p class="muted">季度财务数据模块建设中——后续将在此自动同步公司季度财报数据。</p>
  </div>
  <div class="a-disclaimer">个人研究笔记，仅供学习交流，不构成投资建议。© Hugo Yew</div>
  <a class="back-link" href="../index.html#research">← 返回研究</a>
</div>'''
        out = shell(meta['title'] + ' — Hugo Yew', body, meta['desc'])
        os.makedirs(os.path.join(SITE, 'research'), exist_ok=True)
        with open(os.path.join(SITE, 'research', f'{slug}.html'), 'w', encoding='utf-8') as f:
            f.write(out)
        print('article:', slug)

def build_robots():
    with open(os.path.join(SITE, 'robots.txt'), 'w', encoding='utf-8') as f:
        f.write('User-agent: *\nDisallow: /research/\n')

if __name__ == '__main__':
    with open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(build_index())
    build_articles()
    build_robots()
    print('index built')
