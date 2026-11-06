import base64, json, subprocess, sys

REPO = "Zhiyilang/ai-side-hustle-kit"
PATH = "README.md"
LOCAL = "README.md"

content = open(LOCAL, encoding="utf-8").read()
b64 = base64.b64encode(content.encode("utf-8")).decode("ascii")

# get sha
r = subprocess.run(
    ["gh", "api", f"repos/{REPO}/contents/{PATH}"],
    capture_output=True, text=True,
)
if r.returncode != 0:
    print("FETCH SHA FAIL", r.stderr)
    sys.exit(1)
sha = json.loads(r.stdout)["sha"]

# put
body = json.dumps({
    "message": "docs: 赚钱路线图更正为7条线（补⑥头条图文 ⑦百家号）",
    "content": b64,
    "sha": sha,
    "branch": "main",
})
r2 = subprocess.run(
    ["gh", "api", f"repos/{REPO}/contents/{PATH}", "--method", "PUT",
     "-H", "Content-Type: application/json", "--input", "-"],
    input=body, capture_output=True, text=True,
)
if r2.returncode == 0:
    print("README UPDATED OK")
else:
    print("PUT FAIL", r2.stderr)
    sys.exit(1)
