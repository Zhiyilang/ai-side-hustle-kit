import base64, json, subprocess, os
from urllib.parse import quote

REPO = "Zhiyilang/ai-side-hustle-kit"
ROOT = "D:/Program Files/WorkBuddy/AI黑客松/ai-side-hustle-kit-push"

files = [
    "免费样品/简历模板-免费3套预览.md",
    "免费样品/公众号排版速成.md",
    "免费样品/小红书爆款标题库-50条.md",
    "免费样品/Excel实用模板-2套.md",
    "免费样品/AI短视频脚本模板-5条.md",
    "博客/2026普通人用AI搞钱的10条路.md",
    "博客/AI短视频脚本怎么写.md",
    "README.md",
]

for f in files:
    local = os.path.join(ROOT, f)
    content = open(local, encoding="utf-8").read()
    b64 = base64.b64encode(content.encode("utf-8")).decode("ascii")
    api_path = quote(f, safe="")
    # fetch sha if file already exists (for update)
    r = subprocess.run(["gh", "api", f"repos/{REPO}/contents/{api_path}"],
                       capture_output=True, text=True)
    sha = json.loads(r.stdout).get("sha") if r.returncode == 0 else None
    body = {"message": "content: +5免费样品 +2引流长文 +README样品库",
            "content": b64, "branch": "main"}
    if sha:
        body["sha"] = sha
    r2 = subprocess.run(
        ["gh", "api", f"repos/{REPO}/contents/{api_path}", "--method", "PUT",
         "-H", "Content-Type: application/json", "--input", "-"],
        input=json.dumps(body), capture_output=True, text=True)
    status = "UPDATED" if (r2.returncode == 0 and sha) else (
        "CREATED" if r2.returncode == 0 else "FAIL " + r2.stderr[:160])
    print(f"{f}  ->  {status}")
