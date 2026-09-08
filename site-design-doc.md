# Hugo Yew 个人网站 · 设计与功能文档

> 最后更新：2026-09-08
> 网站地址：https://hugoyew.github.io
> 维护方式：飞书文档维护内容 → 手动触发更新 → 自动构建推送

---

## 一、网站概览

| 项目 | 内容 |
|------|------|
| 定位 | 能力导向的立体职业 profile，替代传统 PDF 简历 |
| 域名 | hugoyew.github.io（GitHub Pages 免费子域名） |
| 技术栈 | 纯静态 HTML/CSS/JS，Python 构建脚本（build.py） |
| 仓库 | github.com/hugoyew/hugoyew.github.io |
| 部署 | GitHub Pages，main 分支 root 目录 |
| 语言 | 简中 / 繁中 / English 三语切换 |
| 设计风格 | 苹果风：浅色、极简、科技感、少字 |

---

## 二、设计规范

### 2.1 配色

| 变量 | 色值 | 用途 |
|------|------|------|
| --bg | #f5f5f7 | 页面背景（浅灰） |
| --bg-elev | #ffffff | 卡片/ elevated 背景 |
| --fg | #1d1d1f | 主文本 |
| --fg-secondary | #6e6e73 | 次要文本 |
| --fg-tertiary | #86868b | 三级文本/标签 |
| --hairline | rgba(0,0,0,0.08) | 分隔线 |
| --accent | #0071e3 | 强调色（苹果蓝） |
| --accent-soft | rgba(0,113,227,0.08) | 强调色浅底 |

### 2.2 字体

- 字体栈：-apple-system, SF Pro, PingFang SC/TC, Segoe UI, Roboto
- 标题：粗体，负字距（letter-spacing: -0.02em）
- 正文：16px，行高 1.6
- 标签/分类：大写，字距 0.1-0.14em

### 2.3 布局原则

- 最大宽度 1080px，居中
- 圆角 18px（卡片），12-14px（小组件）
- 单页连续滚动：Hero → Capabilities → Track Record → Research → Life
- 顶部固定导航（毛玻璃背景）
- 研报内页独立页面，不进导航（半公开）

### 2.4 核心设计理念

> 参考 Masterdoc：核心展现能力，creds 只是论证手段。
> 简洁、苹果风、不要太多字。

---

## 三、功能清单

### 3.1 首页（index.html）

| 模块 | 功能 |
|------|------|
| Hero | 词云星环转动动画 + 职业照 + 名字（三语）+ slogan + 联系方式（email/CN tel/HK tel）+ 跳转目录（中英双语） |
| Capabilities | 4 张能力卡片（IPO执行/并购FA/消费研究/估值建模），每张含 icon + 编号 + 描述 + 证据列表 |
| Track Record | 左右分栏：Investment Banking（5项目）/ Investments（7项目），logo 墙 + 匿名项目用 icon |
| Research | 分三类：个股研究/行业研究/医疗健康，卡片含封面 + 标题 + 描述 + 标签，无价格预览 |
| Life | 5 张生活照瀑布流，模糊背景+清晰前景合成图，艺术字标签 |

### 3.2 研报内页（research/*.html）

| 功能 | 说明 |
|------|------|
| 三语切换 | 简/繁/英，标题/描述/价格面板/执行摘要/章节全部三语 |
| 价格面板 | 个股研报顶部：目标价 → 现价 → 上行空间 |
| 数字卡 | 行业研报顶部：3 个关键市场数据 |
| 执行摘要 | frontmatter summary，项目符号列表 |
| 动态图表 | bar/pie/line/heatmap，CSS 动画，md 中用 :::chart 标记 |
| 统一框架 | 执行摘要 → 画像 → 核心论点 → 关键数据 → 风险 → 总结 → 财务数据（口子） |
| Pending 标记 | 医疗研报估值案例 pending，黄色 banner |

### 3.3 三语系统

- 首页：三个 data-lang-block，JS 切换显示/隐藏
- 研报内页：同样模式，shell 传 lang_switch=True
- 繁体：opencc 自动从简体转换
- 英文：手动配置 title_en/desc_en/summary_en/stats_en

### 3.4 手机端适配

- 断点：640px（主）、380px（超小屏）
- 导航缩小，Hero 重排，卡片单列，价格面板纵向，图表字号缩小

---

## 四、内容维护指南

### 4.1 各板块维护位置

| 板块 | 飞书文档 | 本地源文件 |
|------|---------|-----------|
| 简历页（Hero/能力/经历） | 01 简历（三语） | build.py 中 CAPS/HERO/TIMELINE |
| Track Record | 02 Track Record | build.py 中 logo_wall() |
| 研报 | Research 文件夹各文档 | research_raw/*.md |
| Life | 04 Life | assets/photos/ + build.py life_photos() |
| 联系方式/slogan | 直接告知 | build.py |

### 4.2 更新流程（方案 B）

1. 在飞书文档修改内容
2. 发消息："更新网站"
3. 我拉取飞书最新内容 → 同步到本地 → python3 build.py → git push
4. 等待 30 秒 GitHub Pages 部署 → 线上生效

### 4.3 研报写作规范

- 文件位置：research_raw/{slug}.md
- Frontmatter：title / summary / summary_en / last_updated / ticker（可选）
- 统一框架：执行摘要 → 一、画像 → 二、核心论点 → 三、关键数据与证据 → 四、风险与待验证 → 五、总结
- 图表标记：:::chart bar|标题 / :::chart pie|标题 / :::chart line|标题 / :::chart heatmap|标题
- 图表数据行：标签,数值（heatmap 首行为列标题）
- 财务数据模块：build.py 自动添加，暂为占位

---

## 五、迭代日志

### 2026-09-08
- 手机端适配（640px/380px 断点）
- 研报内页三语切换（标题/价格面板/执行摘要/章节）
- 研究卡片三语化（英文标题/描述/标签）
- 股价/数字从研究卡片预览移除，移到研报内页顶部
- 四篇研报加英文执行摘要 summary_en

### 2026-09-07
- 研究分类重构：个股/行业/医疗三类
- PPMT 加价格面板（目标价/现价/上行）
- 行业研报加数字卡
- 职业照改用原图圆角（不再抠图）
- 生活照改用模糊背景+清晰前景合成
- 医疗研报重写为结论型 + pending banner
- 卡罗特 logo 调大

### 2026-09-06
- NF 标题改为 Wealth of Health 观点型
- PPMT 加 IP 代际热力图（7 IP × 8 年龄段）
- NF 全面脱敏（去除公司信息）
- 词云星环转动动画
- 生活照 A+C 结合（瀑布流+抠图+艺术字）

### 更早
- 网站从 Vercel 迁移到 GitHub Pages
- 单页连续滚动改版（参考 new-frontier/cuktech/anker）
- 能力导向 CV 重做
- 研报成品 HTML + 封面
- 三语切换系统搭建
- 浅色主题
- Track Record 左右分栏 logo 墙

---

## 六、待办与未来计划

| 优先级 | 事项 | 状态 |
|--------|------|------|
| 中 | 研报英文正文完整翻译（目前仅执行摘要） | 待逐篇补充 _en.md |
| 中 | 自动同步管道（飞书改→网站自动更新） | 未搭建，当前用方案 B 手动触发 |
| 低 | 财务数据实时更新模块（每季度自动同步） | 已留口子，工程量大以后做 |
| 低 | 正式域名（hugoyew.com） | 腾讯云港澳证件认证受阻，搁置 |
| 低 | 医疗估值案例更新 | 等用户提供最新 equity story 和估值底稿 |
| 低 | Track Record 各项目角色说明 | 等用户提供 |

---

## 七、技术备注

- 构建命令：cd site && python3 build.py
- 推送命令：GIT_SSL_NO_VERIFY=1 git push origin main（直接 push 会 SSL 握手失败）
- PAT：fine-grained，仅 hugoyew.github.io 仓库，Contents read-write，2026-10-07 过期
- 研报不进导航、robots.txt 禁索引（半公开）
- 图片路径：首页用 assets/xxx，研报内页用 ../assets/xxx
