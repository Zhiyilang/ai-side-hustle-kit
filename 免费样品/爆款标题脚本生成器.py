#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爆款标题 + 30秒脚本生成器（离线版，零依赖，双击即用）

适用：抖音 / 小红书 / 视频号 创作者，做选题和写脚本时一键出稿。
用法：
    python 爆款标题脚本生成器.py --topic "考研英语" --platform douyin
    python 爆款标题脚本生成器.py --topic "减脂餐" --platform xiaohongshu --count 8
    python 爆款标题脚本生成器.py --topic "副业赚钱" --out 草稿.md

不联网、不调任何 API，纯模板引擎，5 秒出 10 个标题 + 一条 30 秒脚本。
"""
import argparse
import os
import sys
from datetime import datetime

# ---------- 知识库（精选高频钩子，非随机拼接） ----------
HOOKS = [
    "别再{verb}了，{topic}其实靠{secret}",
    "我赌你不知道，{topic}的{secret}才是关键",
    "3个被低估的{topic}技巧，第2个绝了",
    "{topic}做到这1点，效果直接翻倍",
    "为什么有人{topic}事半功倍？答案在这",
    "千万别{verb}{topic}，90%的人都踩坑",
    "普通人怎么把{topic}玩明白？照做就行",
    "{topic}圈内人才懂的{secret}，今天说透",
    "从0到1搞懂{topic}，这一篇够了",
    "后悔没早看：{topic}最实用的{secret}",
    "把{topic}讲成人话，看完你就懂了",
    "{topic}不是靠{verb}，靠的是这个思路",
]

VERBS = ["硬背", "乱买", "瞎练", "死磕", "跟风", "硬撑"]
SECRETS = ["底层逻辑", "正确顺序", "隐藏入口", "关键节奏", "底层方法", "真正门槛", "最容易忽略的细节"]

# 30秒脚本结构：黄金3秒 / 痛点 / 方法 / 结果 / 引导
SCRIPT_BEATS = [
    ("0-3s 黄金开头", "用一个反常识结论或提问钩住，不废话", "“{topic}这件事，90%的人都做反了。”"),
    ("3-12s 痛点共鸣", "点出目标人群的真实困境，制造“说的就是我”", "“你是不是也{verb}{topic}，花了时间却没结果？”"),
    ("12-22s 给方法", "给1个具体、可立刻照做的动作", "“记住一个核心：{secret}。比如先__再做__，顺序对了就顺了。”"),
    ("22-28s 晒结果", "用可感知的结果强化信任", "“照这个思路，{topic}效率直接提上来，不用再无效努力。”"),
    ("28-30s 引导互动", "引导点赞收藏或关注，提升完播与涨粉", "“觉得有用点个赞，主页还有更多{topic}干货。”"),
]


def make_titles(topic, count):
    titles = []
    i = 0
    while len(titles) < count:
        h = HOOKS[i % len(HOOKS)]
        t = h.format(topic=topic, verb=VERBS[i % len(VERBS)], secret=SECRETS[i % len(SECRETS)])
        if t not in titles:
            titles.append(t)
        i += 1
        if i > len(HOOKS) * 3:
            break
    return titles[:count]


def make_script(topic):
    lines = []
    for idx, (beat, why, tmpl) in enumerate(SCRIPT_BEATS, 1):
        text = tmpl.format(topic=topic, verb=VERBS[0], secret=SECRETS[0])
        lines.append((beat, why, text))
    return lines


def render_md(topic, platform, titles, script):
    pname = {"douyin": "抖音", "xiaohongshu": "小红书", "shipinhao": "视频号"}.get(platform, platform)
    out = []
    out.append("# 《%s》%s 爆款选题草稿" % (topic, pname))
    out.append("")
    out.append("> 生成时间：%s ｜ 平台：%s ｜ 工具：爆款标题脚本生成器（离线版）" % (
        datetime.now().strftime("%Y-%m-%d %H:%M"), pname))
    out.append("")
    out.append("## 一、10 个候选标题（挑一个做封面）")
    out.append("")
    for i, t in enumerate(titles, 1):
        out.append("%d. %s" % (i, t))
    out.append("")
    out.append("## 二、30 秒成片脚本")
    out.append("")
    for beat, why, text in script:
        out.append("**%s**" % beat)
        out.append("- 作用：%s" % why)
        out.append("- 口播/字幕：%s" % text)
        out.append("")
    out.append("---")
    out.append("> 本草稿由开源工具自动生成，按需改写即可发布。更多模板见仓库付费商品。")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="爆款标题 + 30秒脚本生成器（离线版）")
    ap.add_argument("--topic", required=True, help="你的内容主题，如「考研英语」「减脂餐」")
    ap.add_argument("--platform", default="douyin", choices=["douyin", "xiaohongshu", "shipinhao"], help="目标平台")
    ap.add_argument("--count", type=int, default=10, help="生成标题数量（默认10）")
    ap.add_argument("--out", default="", help="可选：把结果写成 .md 文件")
    args = ap.parse_args()

    titles = make_titles(args.topic, args.count)
    script = make_script(args.topic)
    pname = {"douyin": "抖音", "xiaohongshu": "小红书", "shipinhao": "视频号"}.get(args.platform, args.platform)

    print("=" * 48)
    print("《%s》· %s 爆款草稿" % (args.topic, pname))
    print("=" * 48)
    print("\n【候选标题】")
    for i, t in enumerate(titles, 1):
        print("  %d. %s" % (i, t))
    print("\n【30秒脚本】")
    for beat, why, text in script:
        print("  · %s：%s" % (beat, text))
    print("=" * 48)

    md = render_md(args.topic, args.platform, titles, script)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(md)
        print("\n已写出：%s" % os.path.abspath(args.out))
    else:
        print("\n（加 --out 草稿.md 可保存为文档）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
