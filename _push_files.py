#!/usr/bin/env python3
# 通用推送：把本地文件 PUT 到 GitHub 仓库（自动处理中文路径编码 + 已存在则取 sha 更新）
import base64, json, subprocess, sys, os

REPO = "Zhiyilang/ai-side-hustle-kit"
BRANCH = "main"

def gh_api(method, path, body=None):
    cmd = ["gh", "api", f"repos/{REPO}/contents/{path}", "--method", method,
           "-H", "Content-Type: application/json"]
    if body is not None:
        cmd += ["--input", "-"]
    r = subprocess.run(cmd, input=json.dumps(body) if body else None,
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{method} {path} FAIL: {r.stderr[:300]}")
    return json.loads(r.stdout) if r.stdout else {}

def push(local, remote):
    content = open(local, encoding="utf-8").read()
    b64 = base64.b64encode(content.encode("utf-8")).decode("ascii")
    remote_enc = urllib.parse.quote(remote, safe="/")
    try:
        sha = gh_api("GET", remote_enc).get("sha")
    except Exception:
        sha = None
    body = {"message": f"content: 新增 {os.path.basename(local)}",
            "content": b64, "branch": BRANCH}
    if sha:
        body["sha"] = sha
    gh_api("PUT", remote_enc, body)
    print(f"PUSHED {'UPDATE' if sha else 'CREATE'}: {remote}")

import urllib.parse
if __name__ == "__main__":
    for f in sys.argv[1:]:
        base = os.path.basename(f)
        # 博客文件放到 博客/ 目录
        remote = f"博客/{base}"
        push(f, remote)
