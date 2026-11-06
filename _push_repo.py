#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通过 gh CLI API 通道推送文件到 ai-side-hustle-kit 仓库（绕开挂掉的 git https 代理）。"""
import base64, json, os, subprocess, sys
from urllib.parse import quote

OWNER = "Zhiyilang"
REPO  = "ai-side-hustle-kit"
BRANCH = "main"

FILES = [
    "README.md",
    "免费样品/短剧剧本投稿格式模板.md",
    "免费样品/AI副业起步检查清单.md",
    "免费样品/爆款标题脚本生成器.py",
]

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

def gh(args, input_data=None):
    cmd = ["gh", "api"] + args
    if input_data is not None:
        cmd += ["--input", "-"]
    stdin = input_data.encode("utf-8") if input_data is not None else None
    p = subprocess.run(cmd, input=stdin, capture_output=True)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")

def api_path(path):
    return "repos/%s/%s/contents/%s" % (OWNER, REPO, quote(path, safe="/"))

def get_sha(path):
    code, out, err = gh([api_path(path) + "?ref=" + BRANCH])
    if code != 0:
        return None
    try:
        return json.loads(out).get("sha")
    except Exception:
        return None

def push_file(path, message):
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        print("  [skip] 本地不存在: %s" % path)
        return False
    with open(full, "rb") as f:
        raw = f.read()
    content = base64.b64encode(raw).decode("ascii")
    sha = get_sha(path)
    payload = {"message": message, "content": content, "branch": BRANCH}
    if sha:
        payload["sha"] = sha
    body = json.dumps(payload, ensure_ascii=False)
    code, out, err = gh(["--method", "PUT", api_path(path)], input_data=body)
    if code == 0:
        print("  [OK] %s  (%d bytes, %s)" % (path, len(raw), "update" if sha else "create"))
        return True
    print("  [FAIL] %s: %s" % (path, err[:300]))
    return False

def main():
    print("推送到 %s/%s@%s\n" % (OWNER, REPO, BRANCH))
    ok = 0
    for p in FILES:
        if push_file(p, "feat: 加赚钱路线图 + 2 份免费引流资料(剧本格式模板/副业检查清单)"):
            ok += 1
    print("\n完成：%d/%d 个文件" % (ok, len(FILES)))
    return 0 if ok == len(FILES) else 1

if __name__ == "__main__":
    sys.exit(main())
