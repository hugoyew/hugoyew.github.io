#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build hugoyew.github.io — dark one-pager, capability-driven CV, article-based research."""
import re, os, html

SITE = os.path.dirname(os.path.abspath(__file__))

# ============ markdown -> article html ============
def chart_html(ctype, title, data):
    if not data: return ''
    maxv = max(v for _, v in data)
    title_html = f'<div class="chart-title">{title}</div>' if title else ''
    if ctype == 'bar':
        rows = ''
        for label, value in data:
            pct = value / maxv * 100 if maxv else 0
            rows += f'''<div class="cb-row"><span class="cb-label">{label}</span><div class="cb-track"><div class="cb-fill" style="--target:{pct:.1f}%"></div></div><span class="cb-value">{value:g}</span></div>'''
        return f'<div class="chart chart-bar">{title_html}<div class="cb-body">{rows}</div></div>'
    if ctype == 'pie':
        total = sum(v for _, v in data)
        colors = ['#0066FF', '#4D94FF', '#80B3FF', '#B3D1FF', '#CCE0FF', '#E6F0FF']
        stops = []
        acc = 0
        for i, (label, value) in enumerate(data):
            pct = value / total * 100 if total else 0
            stops.append(f'{colors[i % len(colors)]} {acc:.1f}% {acc+pct:.1f}%')
            acc += pct
        legend = ''
        for i, (label, value) in enumerate(data):
            pct = value / total * 100 if total else 0
            legend += f'<div class="cp-item"><span class="cp-dot" style="background:{colors[i%len(colors)]}"></span><span class="cp-label">{label}</span><span class="cp-pct">{pct:.0f}%</span></div>'
        return f'<div class="chart chart-pie">{title_html}<div class="cp-body"><div class="cp-circle" style="background:conic-gradient({", ".join(stops)})"></div><div class="cp-legend">{legend}</div></div></div>'
    if ctype == 'line':
        w, h = 400, 180
        pad_l, pad_r, pad_t, pad_b = 40, 20, 20, 30
        n = len(data)
        maxv = max(v for _, v in data)
        minv = min(v for _, v in data)
        rng = maxv - minv if maxv != minv else 1
        pts = []
        for i, (label, value) in enumerate(data):
            x = pad_l + (w - pad_l - pad_r) * (i / max(n - 1, 1))
            y = pad_t + (h - pad_t - pad_b) * (1 - (value - minv) / rng)
            pts.append((x, y, label, value))
        poly = ' '.join(f'{x:.1f},{y:.1f}' for x, y, _, _ in pts)
        dots = ''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="#0066FF"><animate attributeName="opacity" from="0" to="1" begin="{0.3+i*0.15}s" dur="0.3s" fill="freeze"/></circle>' for i, (x, y, _, _) in enumerate(pts))
        xlabels = ''.join(f'<text x="{x:.1f}" y="{h-8}" text-anchor="middle" font-size="10" fill="#999">{label}</text>' for x, _, label, _ in pts)
        ylabels = ''
        for j in range(4):
            yy = pad_t + (h - pad_t - pad_b) * (j / 3)
            vv = maxv - rng * (j / 3)
            ylabels += f'<text x="{pad_l-8}" y="{yy+3:.1f}" text-anchor="end" font-size="9" fill="#bbb">{vv:.0f}</text><line x1="{pad_l}" y1="{yy:.1f}" x2="{w-pad_r}" y2="{yy:.1f}" stroke="#eee" stroke-width="0.5"/>'
        path_len = 2000
        return f'<div class="chart chart-line">{title_html}<svg viewBox="0 0 {w} {h}" class="cl-svg">{ylabels}<polyline points="{poly}" fill="none" stroke="#0066FF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="{path_len}" stroke-dashoffset="{path_len}"><animate attributeName="stroke-dashoffset" from="{path_len}" to="0" dur="1.5s" fill="freeze"/></polyline>{dots}{xlabels}</svg></div>'
    if ctype == 'heatmap':
        # data: [(row_label, "val1,val2,..."), ...] — first row is header
        if len(data) < 2: return ''
        # header row: first element is corner label, second is comma-separated col headers
        header_cols = [x.strip() for x in data[0][1].split(',')] if data[0][1] else []
        rows = []
        for label, raw in data[1:]:
            vals = []
            for p in raw.split(','):
                try: vals.append(float(p.strip()))
                except: vals.append(0)
            rows.append((label, vals))
        if not header_cols or not rows: return ''
        def heat_color(v):
            t = max(0, min(100, v)) / 100.0
            r = int(245 + (0 - 245) * t)
            g = int(245 + (102 - 245) * t)
            b = int(247 + (255 - 247) * t)
            return f'rgb({r},{g},{b})'
        def text_color(v):
            return '#fff' if v > 50 else '#555'
        thead = ''.join(f'<th>{c}</th>' for c in header_cols)
        tbody = ''
        for row_label, vals in rows:
            cells = ''
            for v in vals:
                label_text = f'{int(v)}%' if v > 0 else ''
                cells += f'<td style="background:{heat_color(v)};color:{text_color(v)}" data-val="{v}">{label_text}</td>'
            tbody += f'<tr><th class="hm-row">{row_label}</th>{cells}</tr>'
        legend = '<div class="hm-legend"><span>弱</span><div class="hm-bar"></div><span>强</span></div>'
        return f'<div class="chart chart-heatmap">{title_html}<div class="hm-wrap"><table class="hm-table"><thead><tr><th></th>{thead}</tr></thead><tbody>{tbody}</tbody></table>{legend}</div></div>'
    return ''

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
        # chart block :::chart type|title
        if line.strip().startswith(':::chart'):
            if in_list: out.append('</ul>'); in_list = False
            if in_ol: out.append('</ol>'); in_ol = False
            cm = re.match(r'^:::chart\s+(\w+)(?:\|(.+))?$', line.strip())
            ctype = cm.group(1) if cm else 'bar'
            ctitle = cm.group(2) if cm and cm.group(2) else ''
            i += 1
            cdata = []
            while i < len(lines) and not lines[i].strip().startswith(':::'):
                cl = lines[i].strip()
                if cl and ',' in cl:
                    if ctype == 'heatmap':
                        parts = cl.split(',', 1)
                        cdata.append((parts[0].strip(), parts[1].strip() if len(parts) > 1 else ''))
                    else:
                        clabel, cval = cl.split(',', 1)
                        try: cdata.append((clabel.strip(), float(cval.strip())))
                        except: pass
                i += 1
            i += 1  # skip closing :::
            out.append(chart_html(ctype, ctitle, cdata)); continue
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
    'popmart':   dict(title='泡泡玛特会是下一个伟大的 IP 公司吗？',
                      title_en='Is POP MART the next great IP company?',
                      rtype='equity', no='01', src='泡泡玛特研究.md',
                      cover='popmart.jpg', ticker='9992.HK',
                      target_price='HK$172–220', current_price='HK$156.2', price_date='2026-09-07',
                      upside='+10% ~ +41%',
                      desc='IP 投资引擎 × 全球化零售渠道：从效率三角到造星机制的完整拆解。',
                      desc_en='IP investment engine × global retail channel: full teardown from the efficiency triangle to star-making.',
                      slug_label='泡泡玛特 IP 研究', slug_label_en='POP MART IP Research'),
    'wandian':   dict(title='万店连锁：什么样的零售业态能跑通？',
                      title_en='10,000-store chains: which retail formats work?',
                      rtype='sector', no='02', src='万店连锁研究.md',
                      cover='coffee.jpg',
                      stats=[('现制饮品', '¥7,464亿', '2025 市场规模'), ('零食饮料', '¥4.3万亿', '2025 市场规模'), ('连锁百强门店', '28.9万', '2025 年')],
                      stats_en=[('Beverages', '¥746B', '2025 market'), ('Snacks & drinks', '¥4.3T', '2025 market'), ('Top100 chain stores', '289K', '2025')],
                      desc='从蜜雪到瑞幸：万店连锁背后的渠道、供应链与心智三层识别框架。',
                      desc_en='From Mixue to Luckin: a three-layer framework — channel, supply chain, mindshare — for identifying scalable retail formats.',
                      slug_label='万店零售业态', slug_label_en='Wan-dian Retail Formats'),
    'kuoshouji': dict(title='厂商抢滩登陆：我们真的需要更宽的手机吗？',
                      title_en='Wide-phone land grab: do we really need wider phones?',
                      rtype='sector', no='03', src='阔手机研究.md',
                      cover='kuoshouji.jpg',
                      stats=[('全球折叠屏', '1,820万台', '2025 出货'), ('2026E 全球', '2,200万+', 'Omdia 预测'), ('中国市场', '~1,000万台', '2025 出货')],
                      stats_en=[('Global foldables', '18.2M', '2025 shipments'), ('2026E global', '22M+', 'Omdia forecast'), ('China market', '~10M', '2025 shipments')],
                      desc='折叠屏 → 阔手机：品类迁移的早期判断与跟踪。',
                      desc_en='Foldable → wide phone: early judgment and tracking of a category shift.',
                      slug_label='阔手机品类研究', slug_label_en='Wide-phone Category Research'),
    'coffee':    dict(title='精品咖啡：小众风味生意里的价值链机会',
                      title_en='Specialty coffee: where the value sits in a niche flavour business',
                      rtype='sector', no='04', src='精品咖啡研究.md',
                      cover='coffee-specialty.jpg',
                      stats=[('精品咖啡市场', '¥63亿', '2024 规模'), ('CAGR', '~41%', '2022–2024'), ('手冲爱好者', '208.5万', '2024 人群')],
                      stats_en=[('Specialty coffee', '¥6.3B', '2024 size'), ('CAGR', '~41%', '2022–2024'), ('Pour-over users', '2.085M', '2024')],
                      desc='自下而上测算市场规模，沿产业链定位「处理法」这一最具议价权的环节。',
                      desc_en='Bottom-up market sizing, locating "processing" as the strongest pricing-power link along the value chain.',
                      slug_label='精品咖啡研究', slug_label_en='Specialty Coffee Research'),
    'newfrontier': dict(title='Wealth of Health：AI 时代无法被替代的是健康身体',
                        title_en='Wealth of Health: the one thing AI cannot replace',
                        rtype='healthcare', no='05', src='医疗服务研究.md',
                        cover='medical.jpg',
                        stats=[('卫生总费用', '¥9.34万亿', '2025 年'), ('长护险参保', '1.9亿人', '2026 覆盖'), ('60岁以上', '3.2亿', '2025 年末')],
                        stats_en=[('Total health spend', '¥9.34T', '2025'), ('LTCI enrollees', '190M', '2026'), ('Aged 60+', '320M', 'end 2025')],
                        desc='全病程闭环平台的 equity story，与相对估值/TAM 双路径交叉验证（案例已脱敏）。',
                        desc_en='Care-continuum platform equity story, cross-validated by relative and TAM valuations (de-identified case).',
                        slug_label='医疗服务研究', slug_label_en='Healthcare Services Research'),
    'charging':  dict(title='充电配件三强：安克、绿联、酷态科是同一门生意吗？',
                      title_en='Charging trio: are Anker, Ugreen and Cuktech the same business?',
                      rtype='sector', no='06', src='充电配件研究.md',
                      cover='charging.jpg',
                      stats=[('安克毛利率', '49.8%', '2026H1'), ('绿联营收增速', '+53.8%', '2025'), ('A股 PE', '25.8 vs 24.3', '绿联 vs 安克')],
                      stats_en=[('Anker gross margin', '49.8%', '1H26'), ('Ugreen rev. growth', '+53.8%', '2025'), ('A-share PE', '25.8 vs 24.3', 'Ugreen vs Anker')],
                      desc='同一供应链下三种赚钱逻辑：品牌溢价、白牌整合与生态依附；PE 同价，但隐含假设相反。',
                      desc_en='Three profit logics under one supply chain — brand premium, white-label consolidation and ecosystem dependence; same PE, opposite bets.',
                      slug_label='充电配件研究', slug_label_en='Charging Accessories Research'),
    'cleaning':  dict(title='智能清洁三问：什么生意、赚谁的钱、往哪去',
                      title_en='Smart cleaning: what business, whose money, where next?',
                      rtype='sector', no='07', src='智能清洁研究.md',
                      cover='cleaning.jpg',
                      stats=[('双寡头份额', '66.5%', '2026Q2 国内'), ('石头 PEG', '0.40', '全场最低'), ('追觅一级估值', '~¥700亿', 'Pre-IPO')],
                      stats_en=[('Duopoly share', '66.5%', '2Q26 China'), ('Roborock PEG', '0.40', 'lowest'), ('Dreame private val.', '~¥70B', 'Pre-IPO')],
                      desc='双寡头定价期里的四种生意与渠道排他实证；石头是唯一有数字佐证的品牌资产。',
                      desc_en='Four businesses in a duopoly-pricing era and the evidence on channel exclusivity; Roborock is the only brand-equity story backed by numbers.',
                      slug_label='智能清洁研究', slug_label_en='Smart Cleaning Research'),
    'ceocean':   dict(title='中国消费电子出海 2026：什么生意、赚谁的钱、往哪去',
                      title_en='China electronics going global 2026: what business, whose money, where next?',
                      rtype='sector', no='08', src='消费电子出海研究.md',
                      cover='ceocean.jpg',
                      stats=[('覆盖公司', '9 家', '三赛道'), ('影石毛利率', '52.2%→41.4%', '技术被打穿'), ('GoPro 份额', '84%→18%', '份额可取代')],
                      stats_en=[('Companies covered', '9', '3 sectors'), ('Insta360 GM', '52.2%→41.4%', 'tech undercut'), ('GoPro share', '84%→18%', 'share replaced')],
                      desc='充电、影像、清洁三赛道收口：技术、份额、规模都会被抹平，唯有品牌资产最难打穿。',
                      desc_en='Charging, imaging and cleaning in one framework: technology, share and scale all erode — only brand equity is genuinely defensible.',
                      slug_label='消费电子出海研究', slug_label_en='Electronics Going-global Research'),
    'dongpeng':  dict(title='东鹏饮料：杀的是故事，不是能力',
                      title_en='Eastroc Beverage: the story was sold off, not the capability',
                      rtype='equity', no='09', src='东鹏饮料研究.md',
                      cover='dongpeng.jpg', ticker='605499.SH · 9980.HK',
                      stats=[('A 股 PE(TTM)', '17.0x', '近 5 年 0.66% 分位'),
                             ('2026H1 毛利率', '48.36%', '创 6 年新高'),
                             ('Wind 一致目标价', '¥185.70', '较现价 +63%')],
                      stats_en=[('A-share P/E (TTM)', '17.0x', '0.66th pct, 5y'),
                                ('Gross margin, 1H26', '48.36%', '6-year high'),
                                ('Wind consensus target', '¥185.70', '+63% upside')],
                      desc='H 股腰斩、A 股 PE 压到历史 0.66% 分位，毛利率却创 6 年新高——三重验证，Q3 财报定胜负。',
                      desc_en='H-shares halved and A-share P/E hit a 5-year low percentile while gross margin reached a six-year high — three tests, with the Q3 report as the verdict.',
                      slug_label='东鹏饮料研究', slug_label_en='Eastroc Beverage Research'),
}
RTYPES = [
    ('equity', '个股研究', 'Equity Research'),
    ('sector', '行业研究', 'Sector Research'),
    ('healthcare', '医疗健康', 'Healthcare'),
]
SLUG_TITLES = {'popmart':'泡泡玛特 IP 研究','wandian':'万店零售业态',
               'kuoshouji':'阔手机品类研究','coffee':'精品咖啡研究','newfrontier':'医疗服务研究',
               'charging':'充电配件研究','cleaning':'智能清洁研究','ceocean':'消费电子出海研究','dongpeng':'东鹏饮料研究'}

# ============ page shell ============
DISCLAIMER = {
    'zh': '<p class="disc-h">免责声明</p>'
          '<p>本网站由 Hugo Yew（姚颂文）个人运营，所载研究、观点与数据仅代表作者个人见解，不代表其任职机构或任何关联方的立场，亦不构成任何证券要约、招揽、投资建议或专业顾问服务。</p>'
          '<p>内容仅供信息参考与学术交流，不应作为买卖任何证券或金融工具的依据；读者据此操作，风险自担，作者不对因使用本网站内容而产生的任何损失承担责任。</p>'
          '<p>数据与资料来源于作者认为可靠的公开渠道，但作者不保证其准确性、完整性或时效性；目标价、评级与预测均为特定时点的个人研究判断，可能随时变更且不另行通知。过往表现不代表未来收益，投资有风险，决策需谨慎。</p>'
          '<p>本网站内容版权归作者所有，未经书面许可不得转载、摘编或用于商业用途。© Hugo Yew</p>',
    'tw': '<p class="disc-h">免責聲明</p>'
          '<p>本網站由 Hugo Yew（姚頌文）個人營運，所載研究、觀點與數據僅代表作者個人見解，不代表其任職機構或任何關聯方的立場，亦不構成任何證券要約、招攬、投資建議或專業顧問服務。</p>'
          '<p>內容僅供資訊參考與學術交流，不應作為買賣任何證券或金融工具的依據；讀者據此操作，風險自擔，作者不對因使用本網站內容而產生的任何損失承擔責任。</p>'
          '<p>數據與資料來源於作者認為可靠的公開渠道，但作者不保證其準確性、完整性或時效性；目標價、評級與預測均為特定時點的個人研究判斷，可能隨時變更且不另行通知。過往表現不代表未來收益，投資有風險，決策需謹慎。</p>'
          '<p>本網站內容版權歸作者所有，未經書面許可不得轉載、摘編或用於商業用途。© Hugo Yew</p>',
    'en': '<p class="disc-h">Disclaimer</p>'
          '<p>This website is maintained personally by Hugo Yew (Chung Man Yew). All research, views and data are solely the author&rsquo;s personal opinions and do not represent those of his employer or any affiliated entity, and do not constitute an offer, solicitation, investment advice or professional service of any kind.</p>'
          '<p>Content is provided for informational and educational purposes only and should not be relied upon as the basis for buying or selling any security or financial instrument. Readers act on it at their own risk; the author accepts no liability for any loss arising from the use of this content.</p>'
          '<p>Information is compiled from public sources believed to be reliable, but its accuracy, completeness or timeliness is not guaranteed. Target prices, ratings and forecasts are the author&rsquo;s personal research views as of a specific date and may change without notice. Past performance is not indicative of future results; investments carry risk.</p>'
          '<p>All content is &copy; Hugo Yew. No reproduction, excerpt or commercial use is permitted without prior written consent.</p>',
}

# ============ Latest Views (timeline on homepage, above Research) ============
# 维护方式：飞书「最新观点」文档 → 用户发「更新网站」→ 助手拉取后更新本列表并重建。
# 语言策略：简中为主；en 只给标题/标签/一句话摘要（重要条目可全英）。
NOTES = [
    {
        'date': '2026-09',
        'tag': {'zh': '消费 · 个股', 'en': 'Consumer · Single-name'},
        'title': {'zh': '泡泡玛特的估值锚，应从「潮玩公司」切换到「IP 平台」',
                  'en': 'Pop Mart is priced as a toy maker; it should be priced as an IP platform'},
        'body': '单季增长只是表象，核心变量是 IP 代际能否持续更替，把单 IP 生命周期拉长成平台级现金流。当前股价隐含的假设与 IP 平台化路径存在明显错位。',
        'body_en': 'The key variable is not quarterly growth but whether IP generations compound into platform-level cash flows; the market prices Pop Mart like a toy maker, not an IP platform.',
        'slug': 'popmart',
    },
    {
        'date': '2026-09',
        'tag': {'zh': '消费电子 · 出海', 'en': 'Consumer Tech · Going Global'},
        'title': {'zh': '技术、份额、规模都会被抹平，品牌资产是出海最后一道护城河',
                  'en': 'Tech, share and scale get commoditized; brand equity is the last moat in cross-border consumer tech'},
        'body': '出海竞争进入下半场：技术差距、渠道份额、规模成本都会随时间拉平，最终剩下的是品牌资产——对渠道的议价力、对消费者的心智、对价格带的掌控。这也是充电、影像、清洁三赛道头部与跟随者估值分化的根源。',
        'body_en': 'As tech gaps, channel share and scale costs converge, the surviving moat is brand equity — pricing power, mindshare and price-band control; it explains the leader-follower valuation gap.',
        'slug': 'ceocean',
    },
    {
        'date': '2026-09',
        'tag': {'zh': '智能清洁 · 行业', 'en': 'Smart Cleaning · Sector'},
        'title': {'zh': '双寡头定价期，盈利质量比增长斜率更重要；石头 PEG 全场最低',
                  'en': 'A duopoly pricing era: profitability quality beats growth slope, and Roborock is the cheapest on PEG'},
        'body': '国内扫地机进入双寡头定价期（两家合计份额约 66.5%），价格战烈度收敛后，盈利质量比增长斜率更重要。石头 PEG 0.40 为全场最低，且是唯一在线上 / 线下 / 海外三层渠道都有可验证排他性的公司；追觅约 700 亿的一级估值与二级可比存在明显错位。',
        'body_en': 'With ~66.5% combined share, pricing discipline matters more than growth slope; Roborock trades at the lowest PEG (0.40) with verifiable exclusivity across online, offline and overseas channels, while Dreame\'s ~RMB70bn private valuation sits at a clear premium to listed peers.',
        'slug': 'cleaning',
    },
    {
        'date': '2026-09',
        'tag': {'zh': '医疗健康 · 行业', 'en': 'Healthcare · Sector'},
        'title': {'zh': 'AI 时代无法被替代的，是健康的身体',
                  'en': 'Wealth of health: the one asset AI cannot replicate'},
        'body': '当 AI 快速商品化知识与执行力，「健康」反而成为最稀缺的资产。医疗服务投资的核心不是堆砌科室，而是全病程闭环能力——从预防、诊断到院外管理的连续服务，才是长期现金流与壁垒所在。',
        'body_en': 'As AI commoditizes knowledge and execution, health becomes the scarcest asset; the winners in healthcare services build full-pathway care loops rather than stacking departments.',
        'slug': 'newfrontier',
    },
]

def views_html(lang='zh'):
    from opencc import OpenCC
    cc = OpenCC('s2t')
    items = ''
    arrow = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
    for n in NOTES:
        date = n['date']
        tag = n['tag']['zh'] if lang != 'en' else n['tag']['en']
        title = n['title']['zh'] if lang != 'en' else n['title']['en']
        body = n['body'] if lang != 'en' else n.get('body_en', '')
        if lang == 'tw':
            tag = cc.convert(tag); title = cc.convert(title); body = cc.convert(body)
        body_html = f'<p class="v-body">{body}</p>' if body else ''
        link = ''
        if n.get('slug'):
            link_word = {'zh': '阅读研报', 'tw': '閱讀研報', 'en': 'Read the note'}[lang]
            link = f'<a class="v-link" href="research/{n["slug"]}.html">{link_word}{arrow}</a>'
        items += f'''<div class="v-item reveal">
  <div class="v-rail"><span class="v-dot"></span></div>
  <div class="v-card">
    <div class="v-head"><span class="v-date">{date}</span><span class="v-tag">{tag}</span></div>
    <div class="v-title">{title}</div>
    {body_html}
    {link}
  </div>
</div>'''
    return f'<div class="views">{items}</div>'

# ============ Financial panels (quarterly, static; per covered stock) ============
# 维护：财报季由月度访谈触发，人工核对口径后更新本字典并重建。行情为收盘价快照。
# 单位：rev/np 年度序列为「亿元」，英文面板自动换算为 RMB bn（×0.1）。
FIN = {
    'cleaning': {
        'ticker': '688169.SH',
        'name': {'zh': '石头科技 Roborock', 'tw': '石頭科技 Roborock', 'en': 'Roborock (688169.SH)'},
        'price_asof': '2026-09-21',
        'price': '¥118.60',
        'consensus': None,
        'mktcap': {'zh': '307.9 亿元', 'tw': '307.9 億元', 'en': 'RMB 30.8 bn'},
        'rev_h1': {'zh': '100.8 亿元', 'tw': '100.8 億元', 'en': 'RMB 10.1 bn'},
        'np_h1': {'zh': '9.86 亿元', 'tw': '9.86 億元', 'en': 'RMB 0.99 bn'},
        'rev_yoy': '+27.6%', 'np_yoy': '+45.6%',
        'pe': '18.4x', 'valuation3': ('peg', '0.40'), 'gm': '43.3%',
        'rev': [('2021', 58.37), ('2022', 66.29), ('2023', 86.54), ('2024', 119.45), ('2025', 186.95)],
        'np': [('2021', 14.02), ('2022', 11.83), ('2023', 20.51), ('2024', 19.77), ('2025', 13.63)],
    },
    'dongpeng': {
        'ticker': '605499.SH',
        'name': {'zh': '东鹏饮料 Eastroc', 'tw': '東鵬飲料 Eastroc', 'en': 'Eastroc Beverage (605499.SH)'},
        'price_asof': '2026-09-22',
        'price': '¥113.71',
        'consensus': {
            'val': {'zh': '¥185.70', 'tw': '¥185.70', 'en': '¥185.70'},
            'sub': {'zh': 'Wind 一致预期 · 49 家券商', 'tw': 'Wind 一致預期 · 49 家券商', 'en': 'Wind consensus · 49 brokers'},
        },
        'mktcap': {'zh': '817 亿元', 'tw': '817 億元', 'en': 'RMB 81.7 bn'},
        'rev_h1': {'zh': '124.4 亿元', 'tw': '124.4 億元', 'en': 'RMB 12.4 bn'},
        'np_h1': {'zh': '28.67 亿元', 'tw': '28.67 億元', 'en': 'RMB 2.87 bn'},
        'rev_yoy': '+15.9%', 'np_yoy': '+20.7%',
        'pe': '17.0x', 'valuation3': ('divyield', '4.28%'), 'gm': '48.4%',
        'rev': [('2021', 69.78), ('2022', 85.05), ('2023', 112.63), ('2024', 158.39), ('2025', 208.75)],
        'np': [('2021', 11.93), ('2022', 14.41), ('2023', 20.40), ('2024', 33.27), ('2025', 44.15)],
    },
}

def fin_panel_html(slug, lang='zh'):
    f = FIN.get(slug)
    if not f:
        return None
    L = {
        'zh': {'market': '现价（收盘）', 'consensus': '一致预期目标价', 'hugo': '我的目标价', 'pending': '待补充',
               'mktcap': '总市值', 'pe': '市盈率 P/E（TTM）', 'peg': 'PEG（研报口径）', 'divyield': '股息率（TTM · A 股）',
               'revh1': '2026H1 营业收入', 'nph1': '2026H1 归母净利', 'gm': '毛利率（2026H1）',
               'revt': '营业收入（亿元）', 'npt': '归母净利润（亿元）',
               'note': '行情截至 {asof} 收盘；财务为 2026 年中报（报告期截至 2026-06-30）。数据来自公司公告及公开行情（同花顺 / Wind），按季度更新；本表仅供研究参考，不构成投资建议。'},
        'tw': {'market': '現價（收盤）', 'consensus': '一致預期目標價', 'hugo': '我的目標價', 'pending': '待補充',
               'mktcap': '總市值', 'pe': '市盈率 P/E（TTM）', 'peg': 'PEG（研報口徑）', 'divyield': '股息率（TTM · A 股）',
               'revh1': '2026H1 營業收入', 'nph1': '2026H1 歸母淨利', 'gm': '毛利率（2026H1）',
               'revt': '營業收入（億元）', 'npt': '歸母淨利潤（億元）',
               'note': '行情截至 {asof} 收盤；財務為 2026 年中報（報告期截至 2026-06-30）。數據來自公司公告及公開行情（同花順 / Wind），按季度更新；本表僅供研究參考，不構成投資建議。'},
        'en': {'market': 'Market (close)', 'consensus': 'Consensus target', 'hugo': "My target", 'pending': 'Pending',
               'mktcap': 'Market cap', 'pe': 'P/E (TTM)', 'peg': 'PEG (note basis)', 'divyield': 'Div yield (TTM · A)',
               'revh1': 'Revenue, 1H26', 'nph1': 'Net profit, 1H26', 'gm': 'Gross margin, 1H26',
               'revt': 'Revenue (RMB bn)', 'npt': 'Net profit (RMB bn)',
               'note': 'Prices as of {asof} close; financials from the 1H26 report (period ended 2026-06-30). Source: company filings and public market data (Tonghuashun / Wind); updated quarterly. For research reference only — not investment advice.'},
    }[lang]
    scale = 0.1 if lang == 'en' else 1.0
    def conv(rows):
        return [(k, round(v * scale, 2)) for k, v in rows]
    rev_chart = chart_html('bar', L['revt'], conv(f['rev']))
    np_chart = chart_html('bar', L['npt'], conv(f['np']))

    def pricecard(label, val=None, sub='', active=False, pend=False):
        cls = 'fp-card' + (' fp-active' if active else '') + (' fp-pending' if pend else '')
        v = f'<span class="fp-pend">{L["pending"]}</span>' if pend else f'<span class="fp-val">{val}</span>'
        s = f'<div class="fp-sub">{sub}</div>' if sub else ''
        return f'<div class="{cls}"><div class="fp-l">{label}</div>{v}{s}</div>'
    cons = f.get('consensus')
    if cons:
        cons_card = pricecard(L['consensus'], cons['val'][lang], cons['sub'][lang])
    else:
        cons_card = pricecard(L['consensus'], pend=True)
    cards = (pricecard(L['market'], f['price'], f['price_asof'], active=True)
             + cons_card
             + pricecard(L['hugo'], pend=True))

    v3key, v3val = f['valuation3']
    def kpi(label, val, delta=None):
        d = f'<span class="kpi-delta">{delta}</span>' if delta else ''
        return f'<div class="kpi"><div class="kpi-v">{val}{d}</div><div class="kpi-l">{label}</div></div>'
    kpis = (kpi(L['mktcap'], f['mktcap'][lang])
            + kpi(L['pe'], f['pe'])
            + kpi(L[v3key], v3val)
            + kpi(L['revh1'], f['rev_h1'][lang], f['rev_yoy'])
            + kpi(L['nph1'], f['np_h1'][lang], f['np_yoy'])
            + kpi(L['gm'], f['gm']))

    return f'''<div class="fin-panel">
  <div class="fp-row">{cards}</div>
  <div class="kpi-grid">{kpis}</div>
  <div class="fin-charts">{rev_chart}{np_chart}</div>
  <p class="fin-note">{L['note'].format(asof=f['price_asof'])}</p>
</div>'''

def shell(title, body, desc='', lang_switch=False):
    ls = '''<div class="lang-switch" id="lang-switch"><button data-lang="zh" class="active">简</button><button data-lang="tw">繁</button><button data-lang="en">EN</button></div>''' if lang_switch else ''
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="../assets/style.css?v=9">
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
  <button class="burger" id="navToggle" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="navSheet"><span></span><span></span><span></span></button>
</div></nav>
<div class="navsheet" id="navSheet" inert>
  <div class="navsheet__scrim" data-nav-close></div>
  <nav class="navsheet__panel" aria-label="Menu">
    <ul class="navsheet__list">
      <li style="--i:0"><a class="navsheet__link" href="../index.html">CV<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a></li>
      <li style="--i:1"><a class="navsheet__link" href="../index.html#track">Track Record<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a></li>
      <li style="--i:2"><a class="navsheet__link" href="../index.html#research">Research<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a></li>
      <li style="--i:3"><a class="navsheet__link" href="../index.html#life">Life<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a></li>
    </ul>
    <div class="navsheet__foot">
      <a class="navsheet__cta" href="mailto:hugoyewtt@gmail.com">Talk to me<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>
      <div class="navsheet__contact">hugoyewtt@gmail.com<br>(+86) 134-5005-0927 · (+852) 6956-9276</div>
    </div>
  </nav>
</div>
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
<link rel="stylesheet" href="assets/style.css?v=9">
</head>
<body>
<div class="scroll-progress" id="scrollProgress"></div>
{body}
</body>
</html>'''

# ============ capability CV (trilingual) ============
CAPS = {
'zh': [
  ('01', '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="16" y2="17"/></svg>',
   '执行 5+ 港股 IPO 项目全流程',
   '尽职调查 · 招股书撰写 · 投资者沟通 · 估值分析'),
  ('02', '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>',
   '主导跨境并购 Business & Finance 模块',
   '估值分析 · 战略买家分析'),
  ('03', '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
   '覆盖 7+ 项目投资研究与深度分析',
   '投资研究（消费科技 · 新消费 · TMT）· 行业研究 · 公司研究'),
  ('04', '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>',
   '精通估值建模与 Equity Story 构建',
   'DCF · Comps · LBO · Equity Story'),
],
'tw': [
  ('01', '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="16" y2="17"/></svg>',
   '執行 5+ 港股 IPO 項目全流程',
   '盡職調查 · 招股書撰寫 · 投資者溝通 · 估值分析'),
  ('02', '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>',
   '主導跨境併購 Business & Finance 模塊',
   '估值分析 · 戰略買家分析'),
  ('03', '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
   '覆蓋 7+ 項目投資研究與深度分析',
   '投資研究（消費科技 · 新消費 · TMT）· 行業研究 · 公司研究'),
  ('04', '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>',
   '精通估值建模與 Equity Story 構建',
   'DCF · Comps · LBO · Equity Story'),
],
'en': [
  ('01', '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="16" y2="17"/></svg>',
   'Execute 5+ HK IPO deals end-to-end',
   'Due Diligence · Prospectus · Investor Communication · Valuation'),
  ('02', '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>',
   'Lead cross-border M&A Business & Finance',
   'Valuation · Strategic Buyer Analysis'),
  ('03', '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
   'Cover 7+ deals in investment research',
   'Investment Research (Consumer Tech · New Consumer · TMT) · Sector · Company'),
  ('04', '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>',
   'Master valuation modeling & equity story',
   'DCF · Comps · LBO · Equity Story'),
],
}
HERO = {
'zh': dict(slogan='洞察即<span class="hl">价值</span>', name='姚颂文', name2='Hugo Yew'),
'tw': dict(slogan='洞察即<span class="hl">價值</span>', name='姚頌文', name2='Hugo Yew'),
'en': dict(slogan='Insight is <span class="hl">Value</span>', name='Chung Man Yew', name2='Hugo Yew'),
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
EXPERIENCE = {
'zh': {
  'work_label': '工作经历',
  'edu_label': '教育背景',
  'work': [
    ('clsa.png', '中信里昂证券 CLSA', '投资银行部分析师', '2026.06 – 至今', '港股 IPO 执行与跨境并购财务顾问'),
    ('genesis.png', '元生资本', '消费投资实习生', '2025.02 – 2025.09', 'Pre-IPO 投资研究 · 3 起港股 IPO 尽调'),
    ('being.png', '源一资本', '消费投资实习生', '2024.09 – 2025.02', '港股新消费深度研究 · 潮玩行业独立研究'),
  ],
  'edu': [
    ('fisf.png', '复旦大学 国际金融学院', '金融学硕士', '2024.09 – 2026.06', 'FISF'),
    ('lingnan.png', '中山大学 岭南学院', '国际商务学士', '2020.09 – 2024.06', '康乐杯篮球赛冠军队长'),
  ],
},
'tw': {
  'work_label': '工作經歷',
  'edu_label': '教育背景',
  'work': [
    ('clsa.png', '中信里昂證券 CLSA', '投資銀行部分析師', '2026.06 – 至今', '港股 IPO 執行與跨境併購財務顧問'),
    ('genesis.png', '元生資本', '消費投資實習生', '2025.02 – 2025.09', 'Pre-IPO 投資研究 · 3 起港股 IPO 盡調'),
    ('being.png', '源壹資本', '消費投資實習生', '2024.09 – 2025.02', '港股新消費深度研究 · 潮玩行業獨立研究'),
  ],
  'edu': [
    ('fisf.png', '復旦大學 國際金融學院', '金融學碩士', '2024.09 – 2026.06', 'FISF'),
    ('lingnan.png', '中山大學 嶺南學院', '國際商務學士', '2020.09 – 2024.06', '康樂杯籃球賽冠軍隊長'),
  ],
},
'en': {
  'work_label': 'Work Experience',
  'edu_label': 'Education',
  'work': [
    ('clsa.png', 'CITIC CLSA', 'Analyst, Investment Banking', 'Jun 2026 – Present', 'HK IPO execution & cross-border M&A advisory'),
    ('genesis.png', 'Genesis Capital', 'Consumer Investment Intern', 'Feb 2025 – Sep 2025', 'Pre-IPO research · CDD on 3 HK IPO deals'),
    ('being.png', 'Being Capital', 'Consumer Investment Intern', 'Sep 2024 – Feb 2025', 'HK new-consumer deep research · collectibles'),
  ],
  'edu': [
    ('fisf.png', 'Fudan University · FISF', 'MSc Finance', 'Sep 2024 – Jun 2026', ''),
    ('lingnan.png', 'Sun Yat-sen University · Lingnan', 'BSc International Business', 'Sep 2020 – Jun 2024', 'Champion basketball captain'),
  ],
},
}

def life_photos(items):
    cards = ''
    for idx, (img, word, cap, ratio) in enumerate(items):
        cards += f'''<div class="life-card life-card-v2 reveal reveal-d{min(idx+1,4)}" style="aspect-ratio:{ratio};background-image:url(assets/photos/composed/{img})">
  <div class="life-word">{word}</div>
  <div class="life-cap">{cap}</div>
</div>'''
    return f'<div class="life-masonry">{cards}</div>'

def build_index():
    def caps_html(lang):
        cards = ''
        for idx, (num, icon, headline, tags) in enumerate(CAPS[lang]):
            cards += f'''<div class="cap-card tilt-card reveal reveal-d{idx+1}"><div class="cap-head"><div class="cap-icon">{icon}</div><div class="cap-num">{num}</div></div><h3 class="cap-headline">{headline}</h3><div class="cap-tags">{tags}</div></div>'''
        return f'<div class="caps tilt-wrap">{cards}</div>'
    def timeline_html(lang):
        items = ''
        for org, role, date, pts in TIMELINE[lang]:
            right = ''.join(f'<li>{p}</li>' for p in pts) if pts else '<ul></ul>'
            items += f'''<div class="t-item"><div class="t-left"><div class="t-org">{org}</div><div class="t-role">{role}</div><div class="t-date">{date}</div></div><div class="t-right"><ul>{right}</ul></div></div>'''
        return f'<div class="timeline">{items}</div>'
    def experience_html(lang):
        data = EXPERIENCE[lang]
        def exp_group(label, items):
            items_html = ''
            for logo, org, role, date, desc in items:
                desc_html = f'<div class="exp-desc">{desc}</div>' if desc else ''
                items_html += f'''<div class="exp-item">
  <div class="exp-logo"><img src="assets/logos/{logo}" alt="{org}"></div>
  <div class="exp-head"><div class="exp-org">{org}</div><div class="exp-date">{date}</div></div>
  <div class="exp-role">{role}</div>
  {desc_html}
</div>'''
            return f'<div class="exp-group"><div class="exp-group-label">{label}</div><div class="exp-timeline">{items_html}</div></div>'
        return f'<div class="exp-groups">{exp_group(data["work_label"], data["work"])}{exp_group(data["edu_label"], data["edu"])}</div>'
    def logo_wall():
        ICONS = {
          'glasses': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="6" cy="15" r="4"/><circle cx="18" cy="15" r="4"/><path d="M10 15h4M2 15l2-6M22 15l-2-6"/></svg>',
          'beauty': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 3h12l4 6-10 12L2 9z"/></svg>',
          'medical': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="7" width="18" height="14" rx="2"/><path d="M12 11v6M9 14h6M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>',
          'ai': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M9 9l-2 3 2 3M15 9l2 3-2 3M12 7v10"/></svg>',
        }
        ib = [('新乳业', 'newhope.png', 'IPO 执行 · 消费', ''),
              ('某头部 AI 眼镜企业', '', 'H 股 IPO · 消费科技', 'glasses'),
              ('某头部国货美妆', '', 'H 股 IPO · 消费', 'beauty'),
              ('某东南亚龙头医疗服务机构', '', '并购 FA · 医疗', 'medical'),
              ('某国内领先的 AI 驱动软件服务公司', '', 'H 股 IPO · TMT', 'ai')]
        pf = [('宁德时代 CATL', 'catl.png', '2025 港股 IPO 基石投资', ''),
              ('Yarbo', 'yarbo.png', '2025 早期投资', ''),
              ('蜜雪冰城', 'mixue-text.png', '2025 港股 IPO 锚定投资', ''),
              ('古茗', 'guming.png', '2025 港股 IPO 基石投资', ''),
              ('卡罗特 Carote', 'carote.png', '2025 港股 IPO 基石投资', ''),
              ('货拉拉 Lalamove', 'lalamove.png', '覆盖 · 港股 IPO 投资中', ''),
              ('Uwant 友望', 'uwant.png', '覆盖 · 早期投资中', '')]
        def wall(items):
            cards = ''
            for n, img, note, cls in items:
                if cls in ICONS:
                    media = f'<div class="logo-icon">{ICONS[cls]}</div>'
                else:
                    media = f'<img src="assets/logos/{img}" class="{cls}" alt="{n}">'
                cards += f'<div class="logo-card">{media}<div class="co">{n}</div><div class="note">{note}</div></div>'
            return f'<div class="logo-wall">{cards}</div>'
        return f'''<div class="track-cols">
  <div class="track-col reveal reveal-d1"><div class="group-label">Investment Banking</div>{wall(ib)}</div>
  <div class="track-col reveal reveal-d2"><div class="group-label">Investments</div>{wall(pf)}</div>
</div>'''
    def research_grid(lang='zh'):
        from opencc import OpenCC
        cc = OpenCC('s2t')
        out = ''
        for rtype_key, rt_zh, rt_en in RTYPES:
            rt_tw = cc.convert(rt_zh)
            rt_label = {'zh': rt_zh, 'tw': rt_tw, 'en': rt_en}[lang]
            rt_sub = {'zh': rt_en, 'tw': rt_en, 'en': ''}[lang]
            cards = ''
            card_idx = 0
            for slug, meta in RESEARCH.items():
                if meta['rtype'] != rtype_key: continue
                card_idx += 1
                cta_word = {'zh': '阅读全文', 'tw': '閱讀全文', 'en': 'Read'}[lang]
                rcta = f'''<span class="r-cta"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg><span class="r-cta-txt">{cta_word}</span></span>'''
                pending_badge = '<span class="r-pending">PENDING</span>' if meta.get('pending') else ''
                title = meta['title'] if lang != 'en' else meta.get('title_en', meta['title'])
                if lang == 'tw': title = cc.convert(title)
                desc = meta['desc'] if lang != 'en' else meta.get('desc_en', meta['desc'])
                if lang == 'tw': desc = cc.convert(desc)
                slug_label = meta.get('slug_label', SLUG_TITLES.get(slug, slug))
                if lang == 'en': slug_label = meta.get('slug_label_en', slug_label)
                elif lang == 'tw': slug_label = cc.convert(slug_label)
                if meta.get('icon'):
                    icon_svg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="7" width="18" height="14" rx="2"/><path d="M12 11v6M9 14h6M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>'
                    cover = f'''<div class="r-cover r-icon"><div class="r-icon-svg">{icon_svg}</div><div class="r-no">{meta['no']}</div><div class="r-cat">{rt_en}</div>{pending_badge}{rcta}</div>'''
                elif meta.get('cover'):
                    cover = f'''<div class="r-cover r-img" style="background-image:url(assets/covers/{meta['cover']})"><div class="r-no">{meta['no']}</div><div class="r-cat">{rt_en}</div><div class="r-title">{title}</div>{pending_badge}{rcta}</div>'''
                else:
                    cover = f'''<div class="r-cover g1"><div class="r-no">{meta['no']}</div><div class="r-cat">{rt_en}</div><div class="r-title">{title}</div>{pending_badge}{rcta}</div>'''
                cards += f'''<a class="r-card reveal reveal-d{min(card_idx,4)}" href="research/{slug}.html">
  {cover}
  <div class="r-body"><div class="r-title-sm">{title}</div><div class="r-desc">{desc}</div><div class="r-meta"><span>{slug_label}</span><span>→</span></div></div>
</a>'''
            sub_html = f' <span style="color:var(--fg-tertiary);font-weight:400;font-size:13px;">{rt_sub}</span>' if rt_sub else ''
            out += f'''<div class="r-category"><h3>{rt_label}{sub_html}</h3><div class="r-grid">{cards}</div></div>'''
        return out
    def section(ids, tag, title, sub, inner):
        return f'''<div class="section" id="{ids}"><div class="section-tag">{tag}</div><h2 class="section-title">{title}</h2><p class="section-sub">{sub}</p>{inner}</div>'''
    def hero_block(lang):
        h = HERO[lang]
        wc = '''<div class="hero-wordcloud">
      <span class="wc wc-1">Investment Banking</span>
      <span class="wc wc-2">消费研究</span>
      <span class="wc wc-3">IPO</span>
      <span class="wc wc-4">M&amp;A</span>
      <span class="wc wc-5">Valuation</span>
      <span class="wc wc-6">Venture</span>
      <span class="wc wc-7">Cross-border</span>
      <span class="wc wc-8">CLSA</span>
      <span class="wc wc-9">Healthcare</span>
      <span class="wc wc-10">TMT</span>
      <span class="wc wc-11">Consumer &amp; Retail</span>
      <span class="wc wc-12">FISF</span>
      <span class="wc wc-13">SYSU 嶺南</span>
    </div>'''
        arrow_svg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
        m1 = {'zh': 'CLSA · 投行分析师', 'tw': 'CLSA · 投行分析師', 'en': 'CLSA · IB Analyst'}[lang]
        m2 = {'zh': '消费 · TMT · 医疗', 'tw': '消費 · TMT · 醫療', 'en': 'Consumer · TMT · Health'}[lang]
        nav_data = [
          ('#capabilities', 'Capabilities', {'zh': '核心能力', 'tw': '核心能力', 'en': 'Core'}),
          ('#experience', 'Experience', {'zh': '经历', 'tw': '經歷', 'en': 'Journey'}),
          ('#track', 'Track Record', {'zh': '代表性项目', 'tw': '代表性項目', 'en': 'Deals'}),
          ('#research', 'Research', {'zh': '研究', 'tw': '研究', 'en': 'Insights'}),
          ('#life', 'Life', {'zh': '生活之外', 'tw': '生活之外', 'en': 'Beyond'}),
        ]
        hn_links = ''
        for idx_d, (href, en_l, subs) in enumerate(nav_data, start=5):
            sub = subs[lang]
            sub_html = f'<span class="hn-zh">{sub}</span>' if sub else ''
            hn_links += f'''<a class="hn-link hero-anim" style="--d:{idx_d}" href="{href}">
      <span class="hn-col">
        <span class="hn-roll"><span class="hn-roll-i"><span class="hn-en">{en_l}</span><span class="hn-en">{en_l}</span></span></span>
        {sub_html}
      </span>
      <span class="hn-arrow">{arrow_svg}</span>
    </a>'''
        return f'''<div class="hero" id="hero">
  <div class="hero-slogan hero-anim" style="--d:0">{h['slogan']}</div>
  <div class="hero-center">
    {wc}
    <div class="hm hm--l"><span class="hm-dot"></span><span class="hm-label">{m1}</span></div>
    <div class="hm hm--r"><span class="hm-dot"></span><span class="hm-label">{m2}</span></div>
    <div class="hero-photo-cutout parallax-mid hero-anim" style="--d:2" data-speed="0.06"><img src="assets/photos/professional_cutout.png" alt="{h['name']}"></div>
    <div class="hero-name hero-anim" style="--d:3">{h['name']} <span>{h['name2']}</span></div>
  </div>
  <div class="hero-contact hero-anim" style="--d:4">
    <span class="hc-item">hugoyewtt@gmail.com</span>
    <span class="hc-item">(+86) 134-5005-0927</span>
    <span class="hc-item">(+852) 6956-9276</span>
  </div>
  <div class="hero-nav">
    {hn_links}
  </div>
</div>'''
    hero_zh = hero_block('zh'); hero_tw = hero_block('tw'); hero_en = hero_block('en')
    # duplicate hero ids must be unique per language — use data-lang wrappers
    nav = '''<nav><div class="nav-inner">
  <a class="nav-brand" href="index.html">Hugo Yew</a>
  <div class="nav-links">
    <a href="#hero">Home</a>
    <a href="#capabilities">Capabilities</a>
    <a href="#experience">Experience</a>
    <a href="#track">Track Record</a>
    <a href="#research">Research</a>
    <a href="#life">Life</a>
    <div class="lang-switch" id="lang-switch"><button data-lang="zh" class="active">简</button><button data-lang="tw">繁</button><button data-lang="en">EN</button></div>
  </div>
  <button class="burger" id="navToggle" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="navSheet"><span></span><span></span><span></span></button>
</div></nav>'''
    navsheet = '''<div class="navsheet" id="navSheet" inert>
  <div class="navsheet__scrim" data-nav-close></div>
  <nav class="navsheet__panel" aria-label="Menu">
    <ul class="navsheet__list">
      <li style="--i:0"><a class="navsheet__link" href="#capabilities">Capabilities<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a></li>
      <li style="--i:1"><a class="navsheet__link" href="#experience">Experience<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a></li>
      <li style="--i:2"><a class="navsheet__link" href="#track">Track Record<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a></li>
      <li style="--i:3"><a class="navsheet__link" href="#research">Research<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a></li>
      <li style="--i:4"><a class="navsheet__link" href="#life">Life<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a></li>
    </ul>
    <div class="navsheet__foot">
      <a class="navsheet__cta" href="mailto:hugoyewtt@gmail.com">Talk to me<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>
      <div class="navsheet__contact">hugoyewtt@gmail.com<br>(+86) 134-5005-0927 · (+852) 6956-9276</div>
    </div>
  </nav>
</div>'''
    body = f'''{nav}
{navsheet}
<main>
  <div data-lang-block="zh">{hero_zh}</div>
  <div data-lang-block="tw" hidden>{hero_tw}</div>
  <div data-lang-block="en" hidden>{hero_en}</div>

  <div data-lang-block="zh">{section('capabilities','Capabilities','核心能力','中信里昂证券投行部分析师，横跨一级市场投资与二级市场研究，专注消费零售与医疗健康。', caps_html('zh'))}</div>
  <div data-lang-block="tw" hidden>{section('capabilities','Capabilities','核心能力','中信里昂證券投行部分析師，橫跨一級市場投資與二級市場研究，專注消費零售與醫療健康。', caps_html('tw'))}</div>
  <div data-lang-block="en" hidden>{section('capabilities','Capabilities','Core Capabilities','Investment Banking Analyst at CITIC CLSA, spanning primary market investing and secondary research, focused on consumer & retail and healthcare.', caps_html('en'))}</div>

  <div data-lang-block="zh">{section('experience','Experience','经历','职业与教育背景。', experience_html('zh'))}</div>
  <div data-lang-block="tw" hidden>{section('experience','Experience','經歷','職業與教育背景。', experience_html('tw'))}</div>
  <div data-lang-block="en" hidden>{section('experience','Experience','Experience','Career & education.', experience_html('en'))}</div>

  <div data-lang-block="zh">{section('track','Track Record','代表性项目','参与过的关键交易与投资。', logo_wall())}</div>
  <div data-lang-block="tw" hidden>{section('track','Track Record','代表性項目','參與過的關鍵交易與投資。', logo_wall())}</div>
  <div data-lang-block="en" hidden>{section('track','Track Record','Selected Work','Key deals and investments I have been part of.', logo_wall())}</div>

  <div data-lang-block="zh">{section('views','Latest Views','最新观点','最近在想什么：从研究立场出发的观点快照。', views_html('zh'))}</div>
  <div data-lang-block="tw" hidden>{section('views','Latest Views','最新觀點','最近在想什麼：從研究立場出發的觀點快照。', views_html('tw'))}</div>
  <div data-lang-block="en" hidden>{section('views','Latest Views','Latest Views','Quick takes off my research — what I have been thinking about lately.', views_html('en'))}</div>

  <div data-lang-block="zh">{section('research','Research','研究','成体系的研究输出：消费零售、医疗健康与跨行业框架。', research_grid('zh'))}</div>
  <div data-lang-block="tw" hidden>{section('research','Research','研究','成體係的研究輸出：消費零售、醫療健康與跨行業框架。', research_grid('tw'))}</div>
  <div data-lang-block="en" hidden>{section('research','Research','Research','Systematic research output: consumer & retail, healthcare, and cross-industry frameworks.', research_grid('en'))}</div>

  <div data-lang-block="zh">{section('life','Life','生活之外','工作之外的我。', life_photos([('gym.jpg','FITNESS','健身','3/4'),('nyc.jpg','NYC','Biodesign Challenge 纽约决赛','4/5'),('coffee.jpg','COFFEE','手冲咖啡','3/4'),('referee.jpg','REFEREE','国家二级篮球裁判','4/5'),('captain.jpg','CAPTAIN','岭南队 3 号 · 队长','3/4')]))}</div>
  <div data-lang-block="tw" hidden>{section('life','Life','生活之外','工作之外的我。', life_photos([('gym.jpg','FITNESS','健身','3/4'),('nyc.jpg','NYC','Biodesign Challenge 紐約決賽','4/5'),('coffee.jpg','COFFEE','手沖咖啡','3/4'),('referee.jpg','REFEREE','國家二級籃球裁判','4/5'),('captain.jpg','CAPTAIN','嶺南隊 3 號 · 隊長','3/4')]))}</div>
  <div data-lang-block="en" hidden>{section('life','Life','Beyond Work','Life outside the desk.', life_photos([('gym.jpg','FITNESS','Fitness','3/4'),('nyc.jpg','NYC','Biodesign Challenge · NYC finals','4/5'),('coffee.jpg','COFFEE','Pour-over','3/4'),('referee.jpg','REFEREE','National Level II referee','4/5'),('captain.jpg','CAPTAIN','Lingnan #3 · team captain','3/4')]))}</div>
</main>
<footer>
  <div class="footer-disc">
    <div data-lang-block="zh">本网站内容仅供信息参考与学术交流，不构成投资建议；完整免责声明见各研究报告页底。</div>
    <div data-lang-block="tw" hidden>本網站內容僅供資訊參考與學術交流，不構成投資建議；完整免責聲明見各研究報告頁底。</div>
    <div data-lang-block="en" hidden>Content is for informational and educational purposes only and is not investment advice; the full disclaimer appears at the foot of each research note.</div>
  </div>
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

  /* ---- slide-in nav sheet ---- */
  var nbtn = document.getElementById('navToggle');
  var sheet = document.getElementById('navSheet');
  var panel = sheet ? sheet.querySelector('.navsheet__panel') : null;
  var isOpen = false;
  function syncBurgerContrast(){{
    if(!sheet||!panel||!nbtn) return;
    var panelLeft = window.innerWidth - panel.getBoundingClientRect().width;
    var onPanel = nbtn.getBoundingClientRect().right > panelLeft + 4;
    nbtn.classList.toggle('burger--on-panel', isOpen && onPanel);
  }}
  function setOpen(next){{
    if(!sheet||!nbtn||next===isOpen) return;
    isOpen = next;
    if(next) syncBurgerContrast();
    sheet.classList.toggle('is-open', next);
    nbtn.classList.toggle('is-active', next);
    document.body.classList.toggle('nav-open', next);
    nbtn.setAttribute('aria-expanded', next?'true':'false');
    nbtn.setAttribute('aria-label', next?'Close menu':'Open menu');
    if(next) sheet.removeAttribute('inert'); else sheet.setAttribute('inert','');
    if(!next) nbtn.classList.remove('burger--on-panel');
  }}
  if(nbtn&&sheet){{
    nbtn.addEventListener('click', function(){{ setOpen(!isOpen); }});
    sheet.addEventListener('click', function(e){{
      if(e.target.hasAttribute && e.target.hasAttribute('data-nav-close')) setOpen(false);
      else if(e.target.closest('a')) setOpen(false);
    }});
    document.addEventListener('keydown', function(e){{
      if((e.key==='Escape'||e.key==='Esc')&&isOpen){{ setOpen(false); nbtn.focus(); }}
    }});
    window.addEventListener('resize', function(){{ if(isOpen) syncBurgerContrast(); }});
  }}

  /* ---- scroll progress ---- */
  var bar = document.getElementById('scrollProgress');
  function updateBar(){{
    var h = document.documentElement;
    var max = h.scrollHeight - h.clientHeight;
    var pct = max > 0 ? (h.scrollTop / max) * 100 : 0;
    if (bar) bar.style.width = pct + '%';
  }}

  /* ---- reveal on scroll ---- */
  var revealEls = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {{
    var io = new IntersectionObserver(function(entries){{
      entries.forEach(function(e){{
        if (e.isIntersecting) {{ e.target.classList.add('revealed'); io.unobserve(e.target); }}
      }});
    }}, {{ threshold: 0.12, rootMargin: '0px 0px -40px 0px' }});
    revealEls.forEach(function(el){{ io.observe(el); }});
  }} else {{
    revealEls.forEach(function(el){{ el.classList.add('revealed'); }});
  }}

  /* ---- 3D tilt (pointer / desktop only) ---- */
  var canHover = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  if (canHover) {{
    document.querySelectorAll('.tilt-card').forEach(function(card){{
      card.addEventListener('mousemove', function(ev){{
        var r = card.getBoundingClientRect();
        var x = (ev.clientX - r.left) / r.width - 0.5;
        var y = (ev.clientY - r.top) / r.height - 0.5;
        card.style.transform = 'rotateY(' + (x * 6).toFixed(2) + 'deg) rotateX(' + (-y * 6).toFixed(2) + 'deg) translateY(-4px)';
      }});
      card.addEventListener('mouseleave', function(){{ card.style.transform = ''; }});
    }});
  }}

  /* ---- hero parallax (rAF throttled, stable offsetTop, no feedback loop) ---- */
  function docTopOf(el){{
    var t = 0, n = el;
    while (n) {{ t += n.offsetTop; n = n.offsetParent; }}
    return t;
  }}
  var pLayers = Array.prototype.map.call(document.querySelectorAll('[data-speed]'), function(el){{
    return {{ el: el, sp: parseFloat(el.getAttribute('data-speed')) || 0, docTop: docTopOf(el) }};
  }});
  var ticking = false;
  function parallax(){{
    var sy = window.scrollY, vh = window.innerHeight;
    pLayers.forEach(function(l){{
      var delta = sy - (l.docTop - vh * 0.5);
      var ty = Math.max(-36, Math.min(36, delta * l.sp));
      l.el.style.transform = 'translateY(' + ty.toFixed(1) + 'px)';
    }});
    ticking = false;
  }}
  function onScroll(){{
    updateBar();
    if (!ticking) {{ requestAnimationFrame(parallax); ticking = true; }}
  }}
  var resizeT;
  window.addEventListener('resize', function(){{
    clearTimeout(resizeT);
    resizeT = setTimeout(function(){{ pLayers.forEach(function(l){{ l.docTop = docTopOf(l.el); }}); parallax(); }}, 200);
  }});
  window.addEventListener('scroll', onScroll, {{ passive: true }});
  updateBar(); parallax();
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
        _h = re.sub(r'^#{1,4}\s+', '', ln).strip().lower()
        if re.match(r'^#{1,4}\s+', ln) and (_h in keywords or any(k.lower() in _h for k in keywords)):
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
    from opencc import OpenCC
    cc = OpenCC('s2t')
    for slug, meta in RESEARCH.items():
        src_name = meta.get('src', f'{slug}.md')
        src = os.path.join(SITE, 'research_raw', src_name)
        if not os.path.exists(src):
            src = os.path.join(SITE, 'research_raw', f'{slug}.md')
        if not os.path.exists(src):
            continue
        with open(src, encoding='utf-8') as f:
            md = f.read()
        fm = parse_frontmatter(md)
        content_zh = md_to_article(md)
        # traditional: convert md first, then render
        content_tw = md_to_article(cc.convert(md))
        # english: read _en.md if exists
        src_en = os.path.join(SITE, 'research_raw', f'{slug}_en.md')
        if os.path.exists(src_en):
            with open(src_en, encoding='utf-8') as f:
                md_en = f.read()
            content_en = md_to_article(md_en)
            fm_en = parse_frontmatter(md_en)
            summary_en = fm_en.get('summary', fm.get('summary_en', ''))
        else:
            content_en = ''
            summary_en = fm.get('summary_en', '')

        rtype_map = dict((k, (zh, en)) for k, zh, en in RTYPES)

        def article_body(lang):
            if lang == 'en':
                title = meta.get('title_en', meta['title'])
                desc = meta.get('desc_en', meta['desc'])
                rtype_label = rtype_map[meta['rtype']][1]
            elif lang == 'tw':
                title = cc.convert(meta['title'])
                desc = cc.convert(meta['desc'])
                rtype_label = cc.convert(rtype_map[meta['rtype']][0])
            else:
                title = meta['title']
                desc = meta['desc']
                rtype_label = rtype_map[meta['rtype']][0]

            # price panel
            price_panel = ''
            if meta['rtype'] == 'equity' and meta.get('target_price'):
                if lang == 'en':
                    l1, l2, l3 = 'Target Price', 'Last · ' + meta.get('price_date',''), 'Upside'
                elif lang == 'tw':
                    l1, l2, l3 = '目標價', '現價 · ' + meta.get('price_date',''), '上行空間'
                else:
                    l1, l2, l3 = '目标价', '现价 · ' + meta.get('price_date',''), '上行空间'
                price_panel = f'''<div class="price-panel">
  <div class="pp-item"><div class="pp-label">{l1}</div><div class="pp-val pp-target">{meta['target_price']}</div></div>
  <div class="pp-arrow">→</div>
  <div class="pp-item"><div class="pp-label">{l2}</div><div class="pp-val pp-current">{meta['current_price']}</div></div>
  <div class="pp-item"><div class="pp-label">{l3}</div><div class="pp-val pp-upside">{meta.get('upside','')}</div></div>
</div>'''

            # stat cards
            stat_cards = ''
            stats = meta.get('stats_en' if lang == 'en' else 'stats', meta.get('stats', []))
            if stats:
                cards = ''.join(f'<div class="stat-card"><div class="sc-val">{s[1]}</div><div class="sc-label">{cc.convert(s[0]) if lang=="tw" else s[0]}</div><div class="sc-sub">{cc.convert(s[2]) if lang=="tw" else s[2]}</div></div>' for s in stats)
                stat_cards = f'<div class="stat-cards">{cards}</div>'

            # pending banner
            if meta.get('pending'):
                if lang == 'en':
                    pb = 'Valuation case pending update — awaiting latest equity story and valuation model.'
                elif lang == 'tw':
                    pb = '估值案例部分 pending 更新——待最新 equity story 與估值測算底稿。'
                else:
                    pb = '估值案例部分 pending 更新——待最新 equity story 与估值测算底稿。'
                pending_banner = f'<div class="pending-banner">{pb}</div>'
            else:
                pending_banner = ''

            # executive summary
            if lang == 'en':
                summary = summary_en
                exec_title = 'Executive Summary'
            elif lang == 'tw':
                summary = cc.convert(fm.get('summary', ''))
                exec_title = '執行摘要'
            else:
                summary = fm.get('summary', '')
                exec_title = '执行摘要'
            if not summary:
                summary = f'<p>{desc}</p>'
            if summary and all(l.strip().startswith('- ') for l in summary.strip().split('\n') if l.strip()):
                items = ''.join(f'<li>{inline(cc.convert(l.strip()[2:]) if lang=="tw" else l.strip()[2:])}</li>' for l in summary.strip().split('\n') if l.strip())
                summary = f'<ul>{items}</ul>'

            # content
            if lang == 'en':
                content = content_en if content_en else '<p class="muted">Full English translation of detailed analysis in progress — key takeaways are below.</p>'
            elif lang == 'tw':
                content = content_tw
            else:
                content = content_zh

            # conclusion
            if lang == 'en':
                concl_title = 'Conclusion'
                concl_text = section_after(md_en if os.path.exists(src_en) else md, ['conclusion', 'key takeaways', 'summary']) if os.path.exists(src_en) else ''
                if not concl_text:
                    concl_text = '<p class="muted">Conclusion in progress.</p>'
            elif lang == 'tw':
                concl_title = '總結'
                concl_text = section_after(cc.convert(md), ['總結', '結論', '結語', '結論與展望', '核心結論'])
            else:
                concl_title = '总结'
                concl_text = section_after(md, ['总结', '结论', '结语', '结论与展望', '核心结论'])
            if not concl_text:
                if lang == 'en':
                    concl_text = '<p class="muted">Conclusion in progress.</p>'
                elif lang == 'tw':
                    concl_text = '<p class="muted">結論部分整理中——後續將按統一模板補齊。</p>'
                else:
                    concl_text = '<p class="muted">结论部分整理中——后续将按统一模板补齐。</p>'

            # section labels
            if lang == 'en':
                fin_title, fin_text = 'Financials', 'Quarterly financials module in progress — will auto-sync company quarterly results here.'
                back_text, disclaimer = '← Back to Research', DISCLAIMER['en']
            elif lang == 'tw':
                fin_title, fin_text = '財務數據', '季度財務數據模塊建設中——後續將在此自動同步公司季度財報數據。'
                back_text, disclaimer = '← 返回研究', DISCLAIMER['tw']
            else:
                fin_title, fin_text = '财务数据', '季度财务数据模块建设中——后续将在此自动同步公司季度财报数据。'
                back_text, disclaimer = '← 返回研究', DISCLAIMER['zh']
            fin_panel = fin_panel_html(slug, lang)
            fin_block = fin_panel if fin_panel else f'<p class="muted">{fin_text}</p>'

            # hero media
            if meta.get('logo'):
                hero_media = f'<img class="a-logo" src="../assets/logos/{meta["logo"]}" alt="">'
            elif meta.get('cover'):
                hero_media = f'<div class="a-cover" style="background-image:url(../assets/covers/{meta["cover"]})"></div>'
            elif meta.get('icon'):
                icon_svg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="7" width="18" height="14" rx="2"/><path d="M12 11v6M9 14h6M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>'
                hero_media = f'<div class="a-cover a-icon-cover"><div class="a-icon-svg">{icon_svg}</div></div>'
            else:
                hero_media = ''

            return f'''<div class="article-hero">
  {hero_media}
  <div class="a-hd">
    <div class="r-cat">{rtype_label} · {meta['no']}</div>
    <h1>{title}</h1>
    <div class="a-meta">{desc}</div>
  </div>
</div>
<div class="article">
  {pending_banner}
  {price_panel}
  {stat_cards}
  <div class="exec-summary"><h2>{exec_title}</h2>{summary}</div>
  <div class="a-body">
{content}
  </div>
  <div class="conclusion"><h2>{concl_title}</h2>{concl_text}</div>
  <div class="financials">
    <h2>{fin_title}</h2>
    {fin_block}
  </div>
  <div class="a-disclaimer">{disclaimer}</div>
  <a class="back-link" href="../index.html#research">{back_text}</a>
</div>'''

        body = f'''<div data-lang-block="zh">{article_body('zh')}</div>
<div data-lang-block="tw" hidden>{article_body('tw')}</div>
<div data-lang-block="en" hidden>{article_body('en')}</div>
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

  var nbtn = document.getElementById('navToggle');
  var sheet = document.getElementById('navSheet');
  var panel = sheet ? sheet.querySelector('.navsheet__panel') : null;
  var isOpen = false;
  function syncBurger(){{
    if(!sheet||!panel||!nbtn) return;
    var pl = window.innerWidth - panel.getBoundingClientRect().width;
    nbtn.classList.toggle('burger--on-panel', isOpen && nbtn.getBoundingClientRect().right > pl + 4);
  }}
  function setOpen(next){{
    if(!sheet||!nbtn||next===isOpen) return;
    isOpen = next;
    if(next) syncBurger();
    sheet.classList.toggle('is-open', next);
    nbtn.classList.toggle('is-active', next);
    document.body.classList.toggle('nav-open', next);
    nbtn.setAttribute('aria-expanded', next?'true':'false');
    nbtn.setAttribute('aria-label', next?'Close menu':'Open menu');
    if(next) sheet.removeAttribute('inert'); else sheet.setAttribute('inert','');
    if(!next) nbtn.classList.remove('burger--on-panel');
  }}
  if(nbtn&&sheet){{
    nbtn.addEventListener('click', function(){{ setOpen(!isOpen); }});
    sheet.addEventListener('click', function(e){{
      if(e.target.hasAttribute && e.target.hasAttribute('data-nav-close')) setOpen(false);
      else if(e.target.closest('a')) setOpen(false);
    }});
    document.addEventListener('keydown', function(e){{
      if((e.key==='Escape'||e.key==='Esc')&&isOpen){{ setOpen(false); nbtn.focus(); }}
    }});
    window.addEventListener('resize', function(){{ if(isOpen) syncBurger(); }});
  }}
}})();
</script>'''
        page_title = meta.get('title_en', meta['title'])
        out = shell(page_title + ' — Hugo Yew', body, meta.get('desc_en', meta['desc']), lang_switch=True)
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
