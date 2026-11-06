# -*- coding: utf-8 -*-
"""
把 README 里 16 条占位死链（afdian.com/a/你的ID）替换为「邮件下单」链接。

背景：用户尚未注册爱发电，占位链接点了是不存在的页面 —— 访客点第一个发现是死的，
就会认为整个店铺是假的，这是持续损失的信任。改成 mailto 后：
  - 点击直接唤起邮件客户端，主题/正文已预填商品名与价格
  - 走「邮件下单 → 我交付 → 用户微信/支付宝直转收款」，无平台手续费
  - 用户将来注册爱发电后，可用 _wire_afdian.py 一键换回（该脚本已适配 mailto 形态）
"""
import os
import re
import subprocess
import json
import base64
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
README = os.path.join(ROOT, "README.md")
OWNER, REPO, BRANCH = "Zhiyilang", "ai-side-hustle-kit", "main"
MAIL = "someonelikebaku@163.com"

DEAD = "https://afdian.com/a/你的ID"


def build_mailto(name, price):
    subject = "【购买】%s（%s）" % (name, price)
    body = (
        "你好，我想购买「%s」（%s）。\n\n"
        "请告知付款方式（微信 / 支付宝），付款后请发送文件内容。\n\n"
        "（如果有特殊要求也可以写在这里）" % (name, price)
    )
    return "mailto:%s?subject=%s&body=%s" % (
        MAIL, quote(subject), quote(body))


def convert():
    lines = open(README, encoding="utf-8").read().split("\n")
    out = []
    cur_name, cur_price = None, None
    converted = 0
    remaining = 0

    head_re = re.compile(r"^###\s*(\d+)\s*·\s*(.+?)　\s*`([^`]+)`")
    for ln in lines:
        m = head_re.match(ln)
        if m:
            cur_name = m.group(2).strip()
            cur_price = m.group(3).strip()
            out.append(ln)
            continue
        if DEAD in ln:
            if cur_name:
                url = build_mailto(cur_name, cur_price or "")
                out.append("📮 [邮件下单 →](%s)　（微信/支付宝直转，无平台手续费）" % url)
                converted += 1
            else:
                out.append(ln)
                remaining += 1
            continue
        out.append(ln)

    return "\n".join(out), converted, remaining


def gh(args, input_data=None):
    cmd = ["gh", "api"] + args
    if input_data is not None:
        cmd += ["--input", "-"]
    p = subprocess.run(cmd,
                       input=(input_data.encode("utf-8") if input_data else None),
                       capture_output=True)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def push(rel_path, msg):
    raw = open(os.path.join(ROOT, rel_path), "rb").read()
    api = "repos/%s/%s/contents/%s" % (OWNER, REPO, quote(rel_path, safe="/"))
    c0, o0, _ = gh([api + "?ref=" + BRANCH])
    sha = json.loads(o0).get("sha") if c0 == 0 else None
    payload = {"message": msg,
               "content": base64.b64encode(raw).decode("ascii"),
               "branch": BRANCH}
    if sha:
        payload["sha"] = sha
    c, o, e = gh(["--method", "PUT", api],
                 input_data=json.dumps(payload, ensure_ascii=False))
    if c == 0:
        print("  OK  %s（%d 字节）" % (rel_path, len(raw)))
        return True
    print("  FAIL %s: %s" % (rel_path, e[:200]))
    return False


if __name__ == "__main__":
    new, n, rem = convert()
    print("已转换 %d 条；未能识别商品名而保留 %d 条" % (n, rem))
    if n == 0:
        print("无需改动，退出")
    else:
        open(README, "w", encoding="utf-8").write(new)
        print("推送 README.md ...")
        push("README.md",
             "fix: 16 件商品购买链接由占位死链改为邮件下单（预填商品名价格），"
             "爱发电开通前即可成交，无平台手续费")
