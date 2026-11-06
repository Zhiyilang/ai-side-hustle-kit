# -*- coding: utf-8 -*-
"""通过 gh CLI API 通道，把整个商店页仓库同步到 GitHub（绕开 ssh/代理问题）。
用法：python _push_all.py
会按 .gitignore 规则排除内部工具脚本，其余文件逐个 PUT（新增或带 sha 更新）。
"""
import base64, json, os, subprocess, sys
from urllib.parse import quote

OWNER = "Zhiyilang"
REPO = "ai-side-hustle-kit"
BRANCH = "main"
GH = "C:/Program Files/GitHub CLI/gh.exe"

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

# 排除规则（与 .gitignore 对齐）
EXCLUDE_DIRS = {".git", "__pycache__"}
EXCLUDE_FILES = set()
EXCLUDE_PREFIX = ("_push_", "_gen_covers", "_enhance_repo", "_fix_buylinks", "_set_topics", "_topics", ".gitignore")

def should_skip(path):
    parts = path.split(os.sep)
    if any(p in EXCLUDE_DIRS for p in parts):
        return True
    base = os.path.basename(path)
    if base in EXCLUDE_FILES:
        return True
    if base.startswith(EXCLUDE_PREFIX):
        return True
    return False

def collect():
    out = []
    for dirpath, dirnames, filenames in os.walk("."):
        # 原地修剪排除目录
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, ".").replace(os.sep, "/")
            if should_skip(rel):
                continue
            out.append(rel)
    return sorted(out)

def gh_api(method, path, payload=None, query=""):
    # Windows 下用 shell=True + 全路径字符串，避免 list 形式调用 gh.exe 的 404 坑
    # query 单独拼接，避免 quote() 把 ? / = 编码成 %3F/%3D 导致 GET 失败
    endpoint = "repos/%s/%s/contents/%s" % (OWNER, REPO, quote(path, safe="/"))
    if query:
        endpoint += "?" + query
    cmd = '"%s" api --method %s "%s"' % (GH, method, endpoint)
    stdin = None
    if payload is not None:
        cmd += " --input -"
        stdin = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    p = subprocess.run(cmd, shell=True, input=stdin, capture_output=True)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")

def get_sha(path):
    code, out, _ = gh_api("GET", path, query="ref=" + BRANCH)
    if code == 0:
        try:
            return json.loads(out).get("sha")
        except Exception:
            return None
    return None

def push_file(rel):
    full = os.path.join(ROOT, rel)
    with open(full, "rb") as f:
        raw = f.read()
    content = base64.b64encode(raw).decode("ascii")
    sha = get_sha(rel)
    payload = {"message": "chore: 同步商店页（含本地渲染封面）", "content": content, "branch": BRANCH}
    if sha:
        payload["sha"] = sha
    code, out, err = gh_api("PUT", rel, payload)
    if code == 0:
        return True, "update" if sha else "create"
    return False, err[:200]

def main():
    files = collect()
    print("待推送文件 %d 个\n" % len(files))
    ok = 0
    for rel in files:
        good, info = push_file(rel)
        if good:
            ok += 1
            print("  [OK] %s  (%s)" % (rel, info))
        else:
            print("  [FAIL] %s : %s" % (rel, info))
    print("\n完成 %d/%d" % (ok, len(files)))
    return 0 if ok == len(files) else 1

if __name__ == "__main__":
    sys.exit(main())
