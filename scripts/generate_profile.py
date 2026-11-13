#!/usr/bin/env python3
"""Generate lightweight SVG cards for the GitHub profile README."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "data/profile.json").read_text(encoding="utf-8"))
OUT = ROOT / "cards"
OUT.mkdir(exist_ok=True)

BG = "#0d1117"
PANEL = "#111827"
BORDER = "#263244"
TEXT = "#e6edf3"
MUTED = "#9ca3af"
ACCENT = "#a78bfa"
CYAN = "#67e8f9"


def github_profile(username: str) -> dict:
    request = urllib.request.Request(
        f"https://api.github.com/users/{username}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-card-generator"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError):
        return {}


def svg_start(width: int, height: int, title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">',
        '<defs><linearGradient id="glow" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7c3aed"/><stop offset="1" stop-color="#0891b2"/></linearGradient></defs>',
        f'<rect width="{width}" height="{height}" rx="22" fill="{BG}"/>',
        '<circle cx="760" cy="-30" r="210" fill="#7c3aed" opacity=".12"/>',
        '<circle cx="40" cy="260" r="150" fill="#0891b2" opacity=".08"/>',
    ]


def write(name: str, parts: list[str]) -> None:
    parts.append("</svg>")
    (OUT / name).write_text("\n".join(parts) + "\n", encoding="utf-8")


def text(x: int, y: int, value: str, size: int = 16, color: str = TEXT, weight: int = 400) -> str:
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="Segoe UI, Arial, sans-serif" font-size="{size}" font-weight="{weight}">{escape(str(value))}</text>'


def generate() -> None:
    username = CONFIG["username"]
    stats = github_profile(username)
    followers = stats.get("followers", "—")
    public_repos = stats.get("public_repos", "—")
    public_gists = stats.get("public_gists", "—")

    hero = svg_start(900, 250, f'{CONFIG["name"]} — GitHub profile')
    hero += [
        '<rect x="1" y="1" width="898" height="248" rx="21" fill="none" stroke="' + BORDER + '"/>',
        '<rect x="28" y="28" width="5" height="194" rx="3" fill="url(#glow)"/>',
        text(55, 82, "HELLO, WORLD. I'M", 13, CYAN, 700),
        text(55, 135, CONFIG["name"], 42, TEXT, 700),
        text(57, 170, CONFIG["headline"], 17, ACCENT, 600),
        text(57, 202, f'{CONFIG["location"]}  •  {CONFIG["university"]}  •  Class of {CONFIG["graduation"]}', 13, MUTED),
        '<rect x="650" y="62" width="205" height="126" rx="16" fill="' + PANEL + '" stroke="' + BORDER + '"/>',
        text(672, 94, "GITHUB SNAPSHOT", 11, MUTED, 700),
        text(672, 132, str(public_repos), 25, CYAN, 700),
        text(672, 151, "PUBLIC REPOSITORIES", 10, MUTED, 600),
        text(672, 177, f"{followers} followers  •  {public_gists} gists", 11, TEXT),
    ]
    write("hero.svg", hero)

    focus = svg_start(900, 190, "Current learning focus")
    focus += [
        '<rect x="1" y="1" width="898" height="188" rx="21" fill="none" stroke="' + BORDER + '"/>',
        text(32, 48, "CURRENT FOCUS", 13, CYAN, 700),
        text(32, 78, CONFIG["bio"], 14, TEXT),
    ]
    x = 32
    y = 125
    for item in CONFIG["focus"]:
        width = max(112, len(item) * 9 + 30)
        focus.append(f'<rect x="{x}" y="{y-22}" width="{width}" height="36" rx="18" fill="{PANEL}" stroke="{BORDER}"/>')
        focus.append(text(x + 15, y + 1, item, 12, ACCENT, 600))
        x += width + 12
        if x > 760:
            x = 32
            y += 43
    write("focus.svg", focus)

    projects = svg_start(900, 220, "Featured projects")
    projects += [
        '<rect x="1" y="1" width="898" height="218" rx="21" fill="none" stroke="' + BORDER + '"/>',
        text(32, 45, "SELECTED PROJECTS", 13, CYAN, 700),
    ]
    y = 91
    for project in CONFIG["projects"][:2]:
        projects.append(f'<rect x="28" y="{y-28}" width="844" height="52" rx="12" fill="{PANEL}" stroke="{BORDER}"/>')
        projects.append(text(48, y, project["name"], 15, TEXT, 700))
        projects.append(text(48, y + 19, project["description"], 11, MUTED))
        y += 70
    write("projects.svg", projects)


if __name__ == "__main__":
    generate()
