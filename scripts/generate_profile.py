#!/usr/bin/env python3
"""Generate custom SVG cards for the GitHub profile README."""
import json
import urllib.request
import urllib.error
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "data/profile.json").read_text(encoding="utf-8"))
OUT = ROOT / "cards"
OUT.mkdir(exist_ok=True)
BG, PANEL, BORDER = "#0d1117", "#111827", "#263244"
TEXT, MUTED, ACCENT, CYAN = "#e6edf3", "#9ca3af", "#a78bfa", "#67e8f9"

def github_profile(username):
    req = urllib.request.Request(
        f"https://api.github.com/users/{username}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-card-generator"})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError):
        return {}

def start(width, height, title):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">',
        '<defs><linearGradient id="glow" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7c3aed"/><stop offset="1" stop-color="#0891b2"/></linearGradient></defs>',
        f'<rect width="{width}" height="{height}" rx="22" fill="{BG}"/>',
        '<circle cx="760" cy="-30" r="210" fill="#7c3aed" opacity=".12"/>',
        '<circle cx="40" cy="260" r="150" fill="#0891b2" opacity=".08"/>',
        f'<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="21" fill="none" stroke="{BORDER}"/>']

def label(x, y, value, size=16, color=TEXT, weight=400):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="Segoe UI, Arial, sans-serif" font-size="{size}" font-weight="{weight}">{escape(str(value))}</text>'

def save(filename, parts):
    parts.append("</svg>")
    (OUT / filename).write_text("\n".join(parts) + "\n", encoding="utf-8")

def main():
    stats = github_profile(CONFIG["username"])
    hero = start(900, 250, CONFIG["name"] + " GitHub profile")
    hero += [
        '<rect x="28" y="28" width="5" height="194" rx="3" fill="url(#glow)"/>',
        label(55, 82, "HELLO, WORLD. I'M", 13, CYAN, 700),
        label(55, 135, CONFIG["name"], 42, TEXT, 700),
        label(57, 170, CONFIG["headline"], 17, ACCENT, 600),
        label(57, 202, f'{CONFIG["location"]}  •  {CONFIG["university"]}  •  Class of {CONFIG["graduation"]}', 13, MUTED),
        f'<rect x="650" y="62" width="205" height="126" rx="16" fill="{PANEL}" stroke="{BORDER}"/>',
        label(672, 94, "GITHUB SNAPSHOT", 11, MUTED, 700),
        label(672, 132, stats.get("public_repos", "—"), 25, CYAN, 700),
        label(672, 151, "PUBLIC REPOSITORIES", 10, MUTED, 600),
        label(672, 177, f'{stats.get("followers", "—")} followers', 12)]
    save("hero.svg", hero)

    focus = start(900, 190, "Current learning focus")
    focus += [label(32, 48, "CURRENT FOCUS", 13, CYAN, 700),
              label(32, 78, CONFIG["bio"], 14)]
    x, y = 32, 125
    for item in CONFIG["focus"]:
        width = max(112, len(item) * 9 + 30)
        focus.append(f'<rect x="{x}" y="{y-22}" width="{width}" height="36" rx="18" fill="{PANEL}" stroke="{BORDER}"/>')
        focus.append(label(x + 15, y + 1, item, 12, ACCENT, 600))
        x += width + 12
        if x > 760:
            x, y = 32, y + 43
    save("focus.svg", focus)

    projects = start(900, 220, "Featured projects")
    projects.append(label(32, 45, "SELECTED PROJECTS", 13, CYAN, 700))
    y = 91
    for project in CONFIG["projects"][:2]:
        projects.append(f'<rect x="28" y="{y-28}" width="844" height="52" rx="12" fill="{PANEL}" stroke="{BORDER}"/>')
        projects.append(label(48, y, project["name"], 15, TEXT, 700))
        projects.append(label(48, y + 19, project["description"], 11, MUTED))
        y += 70
    save("projects.svg", projects)

if __name__ == "__main__":
    main()
