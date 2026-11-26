"""Builds assets/stats-{light,dark}.svg: total stars, contributions this year, repos built, top languages.

Runs daily in the Latest videos action (GITHUB_TOKEN raises the API limit); works unauthenticated locally.
Stars and languages count only his own repos (forks excluded). Languages = bytes of code in repos pushed in the last 2 years (plus the team repos).
"""
import json
import os
import re
import urllib.request
from collections import Counter
from datetime import date
from html import escape

from theme import MONO, OUT, SANS, THEMES

USER = "Srikanthdongalajsr"
EXTRA_REPOS = ["atliq/guardex-ai", "atliq/recap"]  # team repos he builds; stars count toward his work
LANG_COLORS = {"Python": "#2450e0", "Jupyter Notebook": "#f2a516", "TypeScript": "#3fa7d6",
               "JavaScript": "#e0c341", "HTML": "#e4572e", "CSS": "#9b5de5", "Other": "#8a93a6"}


def get(url, raw=False):
    h = {"User-Agent": "profile-stats", "Accept": "application/vnd.github+json"}
    if os.environ.get("GITHUB_TOKEN") and "api.github.com" in url:
        h["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    body = urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=20).read().decode()
    return body if raw else json.loads(body)


def collect():
    repos = get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
    own = [r for r in repos if not r["fork"]]
    stars = sum(r["stargazers_count"] for r in own)
    for full in EXTRA_REPOS:
        try:
            stars += get(f"https://api.github.com/repos/{full}")["stargazers_count"]
        except Exception:
            pass
    since = f"{date.today().year - 2}-{date.today():%m}"
    recent = [r["full_name"] for r in own if r["pushed_at"] >= since] + EXTRA_REPOS
    langs = Counter()
    for full in recent:  # bytes of code per language, recent work only
        try:
            langs.update(get(f"https://api.github.com/repos/{full}/languages"))
        except Exception:
            pass
    page = get(f"https://github.com/users/{USER}/contributions", raw=True)
    m = re.search(r"([\d,]+)\s+contributions?\s+in the last year", page)
    contrib = int(m.group(1).replace(",", "")) if m else 0
    return dict(stars=stars, contrib=contrib, repos=len(own), langs=langs)


def svg(d, t):
    W, H = 1200, 170
    nums = [(f'{d["stars"]}', "stars on my code"), (f'{d["contrib"]}', "contributions this year"),
            (f'{d["repos"]}', "repos built")]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
           f'aria-label="{d["stars"]} stars, {d["contrib"]} contributions this year, {d["repos"]} repos">',
           f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="{t["bg"]}" stroke="{t["border"]}"/>']
    for i, (n, label) in enumerate(nums):
        x = 44 + i * 210
        out.append(f'<text x="{x}" y="92" font-family="{SANS}" font-size="56" font-weight="800" letter-spacing="-1" fill="{t["accent"]}">{n}</text>')
        out.append(f'<text x="{x}" y="126" font-family="{SANS}" font-size="18" fill="{t["soft"]}">{escape(label)}</text>')
    # top languages: one stacked bar + legend
    top = d["langs"].most_common(4)
    rest = sum(d["langs"].values()) - sum(c for _, c in top)
    if rest:
        top.append(("Other", rest))
    total = sum(c for _, c in top) or 1
    bx, by, bw = 690, 66, 470
    out.append(f'<text x="{bx}" y="48" font-family="{MONO}" font-size="14" letter-spacing="2" fill="{t["faint"]}">TOP LANGUAGES · LAST 2 YEARS</text>')
    out.append(f'<clipPath id="b"><rect x="{bx}" y="{by}" width="{bw}" height="12" rx="6"/></clipPath><g clip-path="url(#b)">')
    x = bx
    for name, c in top:
        w = bw * c / total
        out.append(f'<rect x="{x:.1f}" y="{by}" width="{w + 0.5:.1f}" height="12" fill="{LANG_COLORS.get(name, t["faint"])}"/>')
        x += w
    out.append("</g>")
    lx, ly = bx, by + 46
    for name, c in top:
        label = f"{name} {round(c / total * 100)}%"
        out.append(f'<circle cx="{lx + 5}" cy="{ly - 5}" r="5" fill="{LANG_COLORS.get(name, t["faint"])}"/>'
                   f'<text x="{lx + 16}" y="{ly}" font-family="{SANS}" font-size="17" fill="{t["soft"]}">{escape(label)}</text>')
        lx += 16 + len(label) * 9 + 22
        if lx > bx + bw - 120:
            lx, ly = bx, ly + 28
    out.append("</svg>")
    return "".join(out)


if __name__ == "__main__":
    d = collect()
    for name, t in THEMES.items():
        (OUT / f"stats-{name}.svg").write_text(svg(d, t), encoding="utf-8")
    print({k: v for k, v in d.items()})
