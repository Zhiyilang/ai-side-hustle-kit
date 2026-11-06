# -*- coding: utf-8 -*-
"""增强 ai-side-hustle-kit 仓库可见度：补全 topics + 优化 description + 推送缺失的免费样品。"""
import base64, json, os, subprocess
from urllib.parse import quote

OWNER, REPO, BRANCH = "Zhiyilang", "ai-side-hustle-kit", "main"
ROOT = os.path.dirname(os.path.abspath(__file__))

DESC = ("16件即买即用的AI数字商品(提示词/模板/脚本/源码/手册)+副业工具链。"
        "免费样品引流→爱发电成交，拍下自动发货。含千部计划短剧/抖音/头条/百家号/闲鱼副业路线图。")
TOPICS = ["ai", "aigc", "side-hustle", "digital-products", "chatgpt-prompts",
          "prompt-engineering", "templates", "automation", "tools", "pptx",
          "resume", "mini-program", "xiaohongshu", "ecommerce", "passive-income",
          "short-drama", "ai-art", "content-creation"]

def gh(args, input_data=None):
    cmd = ["gh", "api"] + args
    if input_data is not None:
        cmd += ["--input", "-"]
    p = subprocess.run(cmd, input=(input_data.encode("utf-8") if input_data else None),
                       capture_output=True)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")

# 1) PATCH description + topics（GitHub 以整体替换方式接收 topics）
body = json.dumps({"description": DESC, "topics": TOPICS}, ensure_ascii=False)
c, o, e = gh(["--method", "PATCH", "repos/%s/%s" % (OWNER, REPO)], input_data=body)
print("PATCH repo:", "OK" if c == 0 else "FAIL " + e[:200])

# 2) 推送缺失的免费样品（README 已链接但仓库里没有）
rel = "免费样品/AI绘图提示词-免费10条.md"
full = os.path.join(ROOT, rel)
raw = open(full, "rb").read()
content = base64.b64encode(raw).decode("ascii")
api = "repos/%s/%s/contents/%s" % (OWNER, REPO, quote(rel, safe="/"))
c0, o0, _ = gh([api + "?ref=" + BRANCH])
sha = json.loads(o0).get("sha") if c0 == 0 else None
payload = {"message": "docs: 补发承诺的免费样品(AI绘图提示词-免费10条)+扩充仓库topics提升搜索可见",
           "content": content, "branch": BRANCH}
if sha:
    payload["sha"] = sha
c, o, e = gh(["--method", "PUT", api], input_data=json.dumps(payload, ensure_ascii=False))
print("PUT sample:", "OK (%d bytes)" % len(raw) if c == 0 else "FAIL " + e[:200])
