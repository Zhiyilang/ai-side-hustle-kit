# -*- coding: utf-8 -*-
"""推送 SERVICES.md（新建）+ README.md（更新，插入代做服务入口）到 ai-side-hustle-kit。
目的：绕开"爱发电未注册"这个卡点，开通"邮件接单 + 微信/支付宝直转"的收款通道。
"""
import base64, json, os, subprocess
from urllib.parse import quote

OWNER, REPO, BRANCH = "Zhiyilang", "ai-side-hustle-kit", "main"
ROOT = os.path.dirname(os.path.abspath(__file__))


def gh(args, input_data=None):
    cmd = ["gh", "api"] + args
    if input_data is not None:
        cmd += ["--input", "-"]
    p = subprocess.run(cmd, input=(input_data.encode("utf-8") if input_data else None),
                       capture_output=True)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def push(rel, message):
    full = os.path.join(ROOT, rel)
    if not os.path.isfile(full):
        print("本地文件不存在:", rel)
        return False
    raw = open(full, "rb").read()
    api = "repos/%s/%s/contents/%s" % (OWNER, REPO, quote(rel, safe="/"))
    c0, o0, e0 = gh([api + "?ref=" + BRANCH])
    sha = json.loads(o0).get("sha") if c0 == 0 else None
    payload = {"message": message,
               "content": base64.b64encode(raw).decode("ascii"),
               "branch": BRANCH}
    if sha:
        payload["sha"] = sha
    c, o, e = gh(["--method", "PUT", api], input_data=json.dumps(payload, ensure_ascii=False))
    if c == 0:
        print("OK  %-14s (%s, %d 字节)" % (rel, "更新" if sha else "新建", len(raw)))
        return True
    print("FAIL %-14s %s" % (rel, e[:200]))
    return False


ok = True
ok &= push("PORTFOLIO.md", "feat: 新增作品集页(真实成品清单+可索取样片)，提升接单转化")
ok &= push("SERVICES.md", "docs: 接单页顶部增加作品集入口，支持先看样片后下单")
ok &= push("README.md", "docs: 首页增加作品集入口")

print("---")
print("全部成功" if ok else "存在失败项")
