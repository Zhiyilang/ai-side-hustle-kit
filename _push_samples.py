# -*- coding: utf-8 -*-
import base64, json, subprocess, sys, os
from urllib.parse import quote

OWNER = "Zhiyilang"
REPO = "ai-side-hustle-kit"
BRANCH = "main"

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

def push_file(local_path, repo_path, message):
    if not os.path.exists(local_path):
        print("  [skip] 本地不存在:", local_path)
        return False
    with open(local_path, "rb") as f:
        raw = f.read()
    content = base64.b64encode(raw).decode("ascii")
    sha = get_sha(repo_path)
    payload = {"message": message, "content": content, "branch": BRANCH}
    if sha:
        payload["sha"] = sha
    body = json.dumps(payload, ensure_ascii=False)
    code, out, err = gh(["--method", "PUT", api_path(repo_path)], input_data=body)
    if code == 0:
        print("  [OK] %s  (%s)" % (repo_path, "update" if sha else "create"))
        return True
    print("  [FAIL] %s: %s" % (repo_path, err[:200]))
    return False

msg = "docs: 新增免费样品（赚钱地图一页纸 + 投稿避坑指南）"
push_file("免费样品/AI副业赚钱地图-一页纸.md", "免费样品/AI副业赚钱地图-一页纸.md", msg)
push_file("免费样品/短剧剧本投稿避坑指南.md", "免费样品/短剧剧本投稿避坑指南.md", msg)
