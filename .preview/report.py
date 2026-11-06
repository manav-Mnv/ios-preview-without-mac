"""Writes results/README.md: the page people see when they open the
preview-results branch on GitHub. Also adds a summary to the Actions run."""
import os
import pathlib
import re
import subprocess
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)

repo = os.environ.get("GITHUB_REPOSITORY", "")
sha = os.environ.get("GITHUB_SHA", "")[:7]
run_url = f"https://github.com/{repo}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"
app = os.environ.get("APP_NAME", "your app")
outcome = os.environ.get("BUILD_OUTCOME", "")


def read(name: str) -> str:
    p = OUT / name
    return p.read_text(errors="ignore").strip() if p.exists() else ""


try:
    xcode = subprocess.run(["xcodebuild", "-version"], capture_output=True, text=True).stdout.split("\n")[0]
except Exception:
    xcode = "Xcode"

# Plain-English hints for the errors beginners hit most.
HINTS = [
    (r"cannot find '([^']+)' in scope", "Swift doesn't know `{0}`. Check the spelling (capital letters matter) and that the file defining it is inside your app folder."),
    (r"cannot find type '([^']+)' in scope", "The type `{0}` isn't defined anywhere Swift can see. Check the spelling, or add the file that defines it."),
    (r"no such module '([^']+)'", "`{0}` isn't available here. Only Apple's built-in frameworks work; packages from the internet aren't downloaded yet."),
    (r"expected '\}'|expected '\)'", "A bracket is missing. Count your `{{` and `}}`, or `(` and `)`, near that line."),
    (r"missing return", "A function or computed property promises a value but doesn't `return` one on every path."),
    (r"is only available in iOS (\d+)", "That feature needs iOS {0} or newer. Wrap it in `if #available(iOS {0}, *)` or raise the iOS version in Package.swift."),
    (r"'main' attribute|multiple types marked @main|@main", "Exactly one struct in your app should be marked `@main`."),
    (r"type '([^']+)' does not conform to protocol 'View'", "`{0}` needs a `var body: some View {{ … }}`."),
]


def hint_for(line: str) -> str:
    for pattern, text in HINTS:
        m = re.search(pattern, line)
        if m:
            return text.format(*m.groups())
    return ""


lines = [f"# 📱 Preview: {app}", ""]
lines.append(f"Commit `{sha}` · {xcode} · {datetime.now(timezone.utc).strftime('%d %b %Y, %H:%M UTC')} · [full log]({run_url})")
lines.append("")

setup_error = read("setup-error.txt")
errors = [e for e in read("errors.txt").splitlines() if e.strip()]
shots = sorted(p.name for p in OUT.glob("*.png"))
crashes = sorted(p.name for p in OUT.glob("*crash*"))

if setup_error:
    lines += ["## ❌ Couldn't find your app", "", setup_error, ""]
elif outcome != "success":
    lines += ["## ❌ The build failed", "", f"{len(errors)} error(s). Fix these, then push again.", ""]
    for e in errors[:40]:
        lines.append(f"- `{e[:300]}`")
        h = hint_for(e)
        if h:
            lines.append(f"  - 💡 {h}")
    if not errors:
        lines.append("No error lines were found. Open the full log link above.")
    lines.append("")
else:
    lines += ["## ✅ Built and ran successfully", ""]
    if crashes:
        lines += ["> ⚠️ **The app crashed** while running. The crash reports are in this branch: " + ", ".join(f"`{c}`" for c in crashes), ""]
    if not shots:
        lines += ["No screenshots were captured. Check the full log.", ""]


def table(prefix: str, title: str) -> None:
    light, dark = f"{prefix}-light.png", f"{prefix}-dark.png"
    if light not in shots and dark not in shots:
        return
    width = 280 if prefix == "iphone" else 380
    lines.extend([f"## {title}", "", "| Light | Dark |", "|---|---|"])
    cells = [f'<img src="{f}" width="{width}">' if f in shots else "–" for f in (light, dark)]
    lines.extend([f"| {cells[0]} | {cells[1]} |", ""])


table("iphone", "iPhone")
table("ipad", "iPad")

extra = [s for s in shots if "-screen-" in s]
if extra:
    lines += ["## Your extra screens (from screens.txt)", ""]
    for s in extra:
        w = 280 if s.startswith("iphone") else 380
        label = s.replace(".png", "").replace("-screen-", " · ")
        lines.append(f'<img src="{s}" width="{w}" alt="{label}"> ')
    lines.append("")

if (OUT / "iphone-launch.mp4").exists():
    lines += ["## Video", "", "[▶️ Watch the app start (iphone-launch.mp4)](iphone-launch.mp4)", ""]

devices = read("devices.txt")
if devices:
    lines += ["<sub>Simulators: " + " · ".join(devices.splitlines()) + "</sub>", ""]

warnings = read("warnings.txt")
if warnings:
    lines += ["<details><summary>Warnings</summary>", "", "```", warnings, "```", "</details>", ""]

(OUT / "README.md").write_text("\n".join(lines))

summary = os.environ.get("GITHUB_STEP_SUMMARY")
if summary:
    status = "❌ Couldn't find your app" if setup_error else ("✅ Built and ran" if outcome == "success" else f"❌ Build failed ({len(errors)} errors)")
    with open(summary, "a") as f:
        f.write(f"### {status}\n\n**[Open your screenshots →](https://github.com/{repo}/tree/preview-results)**\n\n")
        for e in errors[:15]:
            f.write(f"- `{e[:200]}`\n")
print("Report written.")
