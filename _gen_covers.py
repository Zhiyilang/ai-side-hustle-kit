# -*- coding: utf-8 -*-
"""本地免费生成 16 张商品封面卡（PIL，纯 CPU，零积分）。"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
FONT = "/c/Windows/Fonts/simhei.ttf"
FONT_BOLD = "/c/Windows/Fonts/msyhbd.ttc"  # index 0 = regular weight of msyh
OUT = os.path.join(ROOT, "商品封面")
os.makedirs(OUT, exist_ok=True)

W, H = 1200, 630

# 产品清单：(序号, 标题, 价格, emoji, 主色RGB)
PRODUCTS = [
    (1,  "AI绘图提示词包-100式",  "¥9.9",  "🎨", (88, 101, 242)),
    (2,  "AI副业起步包-全家桶",   "¥199",  "🚀", (236, 72, 153)),
    (3,  "AI短视频脚本+分镜包-30条","¥39.9","🎬", (250, 130, 49)),
    (4,  "个人作品集网页模板",     "¥99",   "🖥️", (45, 156, 219)),
    (5,  "微信小程序源码-干饭人格鉴定","¥99","📱", (56, 178, 172)),
    (6,  "Excel模板全家桶-5套",   "¥29.9", "📊", (34, 166, 117)),
    (7,  "年终总结PPT模板-10套",  "¥39",   "📑", (241, 136, 5)),
    (8,  "简历模板-5套",          "¥19.9", "📄", (124, 92, 240)),
    (9,  "儿童绘本故事文本包-10篇","¥19.9","📚", (233, 64, 104)),
    (10, "AI素材图精选包-35张",   "¥29.9", "🖼️", (99, 102, 241)),
    (11, "闲鱼商品主图-16张",     "¥9.9",  "🛒", (240, 92, 34)),
    (12, "AI配音样品-3音色",      "¥5",    "🔊", (0, 184, 217)),
    (13, "PPT样品-同声路演-8页",  "¥9.9",  "📽️", (163, 78, 230)),
    (14, "公众号排版模板-3套",    "¥19.9", "✍️", (230, 80, 80)),
    (15, "小红书封面模板+标题库", "¥19.9", "📕", (240, 60, 90)),
    (16, "AI绘画实战手册",        "¥29.9", "🖌️", (54, 120, 246)),
]

def get_font(size, bold=False):
    try:
        if bold:
            return ImageFont.truetype(FONT_BOLD, size)
        return ImageFont.truetype(FONT, size)
    except Exception:
        return ImageFont.load_default()

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def gradient(c1, c2):
    img = Image.new("RGB", (W, H), c1)
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        col = lerp(c1, c2, t)
        for x in range(W):
            px[x, y] = col
    return img

def wrap_cjk(text, font, max_w):
    lines, cur = [], ""
    for ch in text:
        test = cur + ch
        if font.getlength(test) > max_w and cur:
            lines.append(cur); cur = ch
        else:
            cur = test
    if cur:
        lines.append(cur)
    return lines

def make(pidx, title, price, emoji, accent):
    base = lerp(accent, (18, 22, 48), 0.62)        # 深色渐变底
    top = lerp(accent, (60, 66, 120), 0.35)
    img = gradient(base, top)
    d = ImageDraw.Draw(img)

    # 顶部品牌条
    d.text((54, 46), "AI 副业工具箱 · 数字商品", font=get_font(30), fill=(255, 255, 255))
    d.rectangle([54, 96, 54 + 70, 100], fill=accent)

    # 序号圆牌（不依赖 emoji 字体，纯数字徽章）
    d.ellipse([780, 70, 780 + 210, 70 + 210], fill=(255, 255, 255))
    num = "%02d" % pidx
    nf = get_font(120, bold=True)
    bb = d.textbbox((0, 0), num, font=nf)
    nw, nh = bb[2] - bb[0], bb[3] - bb[1]
    d.text((780 + 105 - nw / 2, 70 + 105 - nh / 2 - 6), num, font=nf, fill=accent)

    # 标题（换行，最多 3 行）
    title_font = get_font(58, bold=True)
    lines = wrap_cjk(title, title_font, W - 140)[:3]
    y = 180
    for ln in lines:
        d.text((70, y), ln, font=title_font, fill=(255, 255, 255))
        y += 74

    # 价格徽章
    bw, bh = 260, 96
    bx, by = W - bw - 54, H - bh - 54
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=24, fill=accent)
    d.text((bx + 30, by + 22), "到手价", font=get_font(26), fill=(255, 255, 255))
    d.text((bx + 30, by + 50), price, font=get_font(46, bold=True), fill=(255, 255, 255))

    # 副标
    d.text((70, H - 70), "即买即用 · 微信/支付宝直转 · 无手续费", font=get_font(26), fill=(220, 224, 245))

    fn = "%02d-%s-封面.png" % (pidx, title)
    img.save(os.path.join(OUT, fn))
    return fn

ok = 0
for p in PRODUCTS:
    try:
        fn = make(*p)
        ok += 1
        print("  [OK] %s" % fn)
    except Exception as e:
        print("  [FAIL] %s: %s" % (p[1], e))
print("\n完成 %d/%d 张封面" % (ok, len(PRODUCTS)))
