# -*- coding: utf-8 -*-
"""把 博客/*.md 转成带排版 + 转化条的 HTML 页，挂进 GitHub Pages 漏斗。
用法：python _gen_blog_html.py
输出：博客/<同名>.html  +  博客/index.html(博客首页)
"""
import os, re, html

BLOG_DIR = os.path.dirname(os.path.abspath(__file__))
SITE = "https://zhiyilang.github.io/ai-side-hustle-kit/"
REPO = "https://github.com/Zhiyilang/ai-side-hustle-kit"
BUY  = "https://afdian.com/u/bfad2caacd0011f184d55254001e7c00"
MAIL = "someonelikebaku@163.com"

# 每篇一句话简介（用于博客首页）
SUMMARY = {
    "2026-AI副业避坑指南-普通人最易踩的8个坑": "普通人做 AI 副业最容易踩的 8 个坑，逐条拆解怎么绕开。",
    "2026普通人用AI搞钱的10条路": "不报课、动手就能跑的 10 条 AI 搞钱路径，按确定性排序。",
    "AIGC版权与平台规则避坑-2026实战": "AIGC 版权、平台规则、AI 声明怎么写才不踩雷。",
    "AI短视频脚本怎么写": "AI 短视频脚本的结构化写法，附可直接改的模板。",
    "AI简历怎么写-2026实战指南": "2026 用 AI 写简历的实战方法，避开海投石沉大海。",
    "Excel效率模板与函数实战": "常用 Excel 效率模板与函数，办公提效直接套。",
    "公众号从0涨到1000粉实操": "公众号从 0 到 1000 粉的实操路径，不买粉不做号。",
    "公众号排版从0到1": "公众号排版从 0 到 1 的可复制流程与模板。",
    "小红书爆款笔记怎么写-2026实战": "小红书爆款笔记的选题、标题、结构写法，2026 实测。",
}

NAV = f'''
<header class="topnav">
  <a class="brand" href="{SITE}index.html">AI 副业工具箱</a>
  <nav>
    <a href="{SITE}index.html">首页</a>
    <a href="{SITE}SERVICES.md">价目表</a>
    <a class="cta" href="{BUY}" target="_blank" rel="noopener">去购买</a>
  </nav>
</header>'''

FOOTER_CTA = f'''
<section class="cta-box">
  <h3>想要现成模板 / 提示词 / 脚本？</h3>
  <p>16 件 AI 数字商品（提示词包、简历/PPT/Excel 模板、短视频脚本、公众号排版、小红书标题库等），
  爱发电托管自动发货，¥5 起；免费样品在 GitHub 仓库 <code>免费样品/</code> 目录，无需注册直接下。</p>
  <div class="cta-btns">
    <a class="btn primary" href="{BUY}" target="_blank" rel="noopener">👉 爱发电店铺（自动发货）</a>
    <a class="btn" href="{REPO}" target="_blank" rel="noopener">GitHub 仓库（含免费样品）</a>
    <a class="btn" href="mailto:{MAIL}">商务/定制：{MAIL}</a>
  </div>
</section>'''

CSS = '''
<style>
:root{--blue:#2f6fed;--ink:#1f2430;--mut:#6b7280;--line:#e6e8ee;--bg:#f6f8fc;}
*{box-sizing:border-box;}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
 color:var(--ink);background:var(--bg);line-height:1.75;}
.topnav{display:flex;align-items:center;justify-content:space-between;padding:14px 20px;
 background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:10;}
.topnav .brand{font-weight:800;color:var(--blue);text-decoration:none;font-size:18px;}
.topnav nav a{margin-left:14px;color:var(--ink);text-decoration:none;font-size:15px;}
.topnav nav a.cta{background:var(--blue);color:#fff;padding:6px 14px;border-radius:8px;font-weight:600;}
.wrap{max-width:760px;margin:0 auto;padding:28px 20px 60px;background:#fff;min-height:60vh;}
.wrap h1{font-size:26px;line-height:1.35;margin:.2em 0 .6em;}
.wrap h2{font-size:21px;margin:1.6em 0 .6em;padding-left:10px;border-left:4px solid var(--blue);}
.wrap h3{font-size:18px;margin:1.3em 0 .5em;}
.wrap p{margin:.7em 0;}
.wrap ul,.wrap ol{padding-left:1.4em;margin:.6em 0;}
.wrap li{margin:.35em 0;}
.wrap blockquote{margin:1em 0;padding:12px 16px;background:#f0f4ff;border-left:4px solid var(--blue);
 border-radius:8px;color:#33415c;}
.wrap code{background:#eef1f6;padding:2px 6px;border-radius:5px;font-size:.92em;}
.wrap a{color:var(--blue);}
.wrap hr{border:none;border-top:1px solid var(--line);margin:1.6em 0;}
.wrap img{max-width:100%;}
.cta-box{margin-top:40px;background:linear-gradient(135deg,#eef3ff,#f7f0ff);border:1px solid #d9e2ff;
 border-radius:14px;padding:22px 20px;text-align:center;}
.cta-box h3{margin-top:0;}
.cta-btns{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-top:14px;}
.btn{display:inline-block;padding:10px 16px;border-radius:10px;background:#fff;border:1px solid #c9d4ee;
 color:var(--ink);text-decoration:none;font-weight:600;font-size:14px;}
.btn.primary{background:var(--blue);color:#fff;border-color:var(--blue);}
.hub{display:grid;gap:14px;}
.card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px 18px;text-decoration:none;color:inherit;display:block;}
.card:hover{border-color:var(--blue);box-shadow:0 4px 16px rgba(47,111,237,.08);}
.card h3{margin:0 0 6px;font-size:17px;color:var(--blue);}
.card p{margin:0;color:var(--mut);font-size:14px;}
</style>'''

def md_to_html(md: str) -> str:
    lines = md.split("\n")
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        # 标题
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>"); i += 1; continue
        # 分割线
        if re.match(r"^\s*---\s*$", line):
            out.append("<hr>"); i += 1; continue
        # 引用块
        if line.lstrip().startswith(">"):
            buf = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                buf.append(lines[i].lstrip()[1:].strip()); i += 1
            out.append("<blockquote>" + inline(" ".join(buf)) + "</blockquote>"); continue
        # 列表
        if re.match(r"^\s*[-*]\s+", line) or re.match(r"^\s*\d+\.\s+", line):
            buf, ordered = [], bool(re.match(r"^\s*\d+\.\s+", line))
            while i < len(lines) and (re.match(r"^\s*[-*]\s+", lines[i]) or re.match(r"^\s*\d+\.\s+", lines[i])):
                item = re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i])
                buf.append(f"<li>{inline(item)}</li>"); i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(buf) + f"</{tag}>"); continue
        # 空行
        if not line.strip():
            i += 1; continue
        # 段落（合并连续非空行）
        buf = [line]
        while i + 1 < len(lines) and lines[i+1].strip() and not re.match(r"^(#{1,6}\s|>\s|\s*[-*]\s|\s*\d+\.\s|^\s*---\s*$)", lines[i+1]):
            buf.append(lines[i+1]); i += 1
        out.append("<p>" + inline(" ".join(buf)) + "</p>"); i += 1
    return "\n".join(out)

def inline(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s

def build_page(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | AI 副业工具箱</title>
<meta name="description" content="{title}——AI 副业实战干货，动手就能做。">
{CSS}</head><body>{NAV}
<main class="wrap">
{body}
{FOOTER_CTA}
</main></body></html>"""

def main():
    files = [f for f in os.listdir(BLOG_DIR) if f.endswith(".md")]
    cards = []
    for f in files:
        base = f[:-3]
        with open(os.path.join(BLOG_DIR, f), encoding="utf-8") as fh:
            md = fh.read()
        title = (re.match(r"^#\s+(.*)$", md) or re.match(r"^#\s*(.*)", md)).group(1).strip()
        body = md_to_html(md)
        html_out = build_page(title, body)
        out_path = os.path.join(BLOG_DIR, base + ".html")
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(html_out)
        desc = SUMMARY.get(base, title)
        cards.append((base + ".html", title, desc))
        print(f"  ✓ {base}.html  ({len(body)} chars)")
    # 博客首页
    hub_cards = "\n".join(
        f'<a class="card" href="{h}"><h3>{t}</h3><p>{d}</p></a>' for h, t, d in cards)
    hub = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI 副业干货博客 | AI 副业工具箱</title>
<meta name="description" content="AI 副业实战干货：避坑、搞钱路径、脚本、排版、涨粉。">
{CSS}</head><body>{NAV}
<main class="wrap">
<h1>AI 副业干货博客</h1>
<p>不卖课、不割韭菜。只写动手就能跑的 AI 副业实战。按确定性排序，先跑通一条再复制。</p>
<div class="hub">
{hub_cards}
</div>
{FOOTER_CTA}
</main></body></html>"""
    with open(os.path.join(BLOG_DIR, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(hub)
    print(f"  ✓ 博客首页 index.html  ({len(cards)} 篇)")

if __name__ == "__main__":
    main()
