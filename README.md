# Hugo Yew — Personal Site

个人简历网站 · 由飞书文档自动生成。

## 站点结构

- `index.html` — CV（简中 / 繁中 / English 三语）
- `track-record.html` — Track Record logo 墙（投行 + 投资）
- `research.html` — 研报列表（半公开，不进导航、不索引）
- `life.html` — Life（占位）
- `assets/` — 样式与 logo 资源

## 内容源（飞书维护中心）

网站内容维护在飞书「Career Site」文件夹，所有修改在飞书完成，网站由同步脚本自动更新。

## 构建

```bash
python3 build.py   # 从 resume.md 等源文件生成 HTML
```

同步管道（飞书 → 网站）见后续配置。
