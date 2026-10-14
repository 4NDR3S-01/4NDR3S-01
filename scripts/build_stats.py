#!/usr/bin/env python3
"""Genera assets/stats.svg con datos reales de la API GraphQL de GitHub.

Uso:  GITHUB_TOKEN=... python3 scripts/build_stats.py <usuario> <salida.svg>
      python3 scripts/build_stats.py --sample <salida.svg>   (datos de ejemplo, para previsualizar)
"""
import datetime as dt
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from build_assets import (ACCENT, BG1, BG2, BORDER_SURGE, BRIGHT, DESC, DIM2, FONT, HOT, SOFT,  # noqa: E402
                          esc, glow, running_light, svg)

QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    pullRequests { totalCount }
    issues { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}"""


def fetch(login):
    token = os.environ["GITHUB_TOKEN"]
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-stats"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(data["errors"])
    return data["data"]["user"]


def summarize(u):
    repos = u["repositories"]["nodes"]
    langs = {}
    for repo in repos:
        for e in repo["languages"]["edges"]:
            n = e["node"]["name"]
            langs.setdefault(n, [0, e["node"]["color"] or BRIGHT])
            langs[n][0] += e["size"]
    total = sum(v[0] for v in langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:5]

    cc = u["contributionsCollection"]
    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    today = dt.date.today().isoformat()
    days = [d for d in days if d["date"] <= today]
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        longest = max(longest, run)
    current = 0
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"]:
            current += 1
        elif i == 0:
            continue          # hoy aún sin contribuciones no rompe la racha
        else:
            break

    return {
        "activity": [
            ("Commits (último año)", cc["totalCommitContributions"] + cc["restrictedContributionsCount"]),
            ("Pull requests", u["pullRequests"]["totalCount"]),
            ("Issues", u["issues"]["totalCount"]),
            ("Repositorios", u["repositories"]["totalCount"]),
            ("Estrellas recibidas", sum(r["stargazerCount"] for r in repos)),
        ],
        "langs": [(n, v[0] / total * 100, v[1]) for n, (v) in top],
        "big": [
            (cc["contributionCalendar"]["totalContributions"], "contribuciones", "ÚLTIMO AÑO"),
            (current, "días", "RACHA ACTUAL"),
            (longest, "días", "RACHA MÁS LARGA"),
        ],
    }


SAMPLE = {
    "activity": [("Commits (último año)", 812), ("Pull requests", 46), ("Issues", 12),
                 ("Repositorios", 18), ("Estrellas recibidas", 11)],
    "langs": [("TypeScript", 71.2, "#3178c6"), ("PHP", 9.4, "#4F5D95"), ("Kotlin", 8.1, "#A97BFF"),
              ("Blade", 6.3, "#f7523f"), ("JavaScript", 5.0, "#f1e05a")],
    "big": [(1024, "contribuciones", "ÚLTIMO AÑO"), (9, "días", "RACHA ACTUAL"), (31, "días", "RACHA MÁS LARGA")],
}


def fmt(n):
    return f"{n:,}".replace(",", ".")


def render(s):
    w, h = 900, 350
    act = []
    for i, (lbl, n) in enumerate(s["activity"]):
        y = 96 + i * 26
        b = 0.15 + i * 0.08
        act.append(f"""
    <g opacity="0">
      <animate attributeName="opacity" values="0;1" dur=".45s" begin="{b:.2f}s" fill="freeze"/>
      <rect x="44" y="{y - 9}" width="7" height="7" fill="{BRIGHT}" transform="rotate(45 47.5 {y - 5.5})"/>
      <text x="62" y="{y}" class="lbl">{esc(lbl)}</text>
      <text x="410" y="{y}" text-anchor="end" class="num">{fmt(n)}</text>
    </g>""")

    langs = []
    bar_x, bar_w = 490, 300
    for i, (name, pct, color) in enumerate(s["langs"]):
        y = 96 + i * 26
        bw = max(bar_w * pct / 100, 3)
        b = 0.3 + i * 0.12
        langs.append(f"""
    <g opacity="0">
      <animate attributeName="opacity" values="0;1" dur=".4s" begin="{b:.2f}s" fill="freeze"/>
      <circle cx="{bar_x + 4}" cy="{y - 5}" r="4" fill="{color}"/>
      <text x="{bar_x + 14}" y="{y}" class="lbl">{esc(name)}</text>
      <text x="860" y="{y}" text-anchor="end" class="pct">{pct:.1f}%</text>
      <rect x="{bar_x + 120}" y="{y - 9}" width="{bar_w - 120 - 10}" height="6" rx="3" fill="#1f0f33"/>
      <rect x="{bar_x + 120}" y="{y - 9}" width="0" height="6" rx="3" fill="url(#bar)">
        <animate attributeName="width" values="0;{(bar_w - 130) * pct / 100:.1f}" dur="1.2s" begin="{b:.2f}s"
                 calcMode="spline" keySplines=".2 .7 .3 1" fill="freeze"/>
      </rect>
    </g>""")

    big = []
    for i, (n, unit, cap) in enumerate(s["big"]):
        cx = 150 + i * 300
        flame = ""
        if i == 1:
            flame = f"""
      <path d="M{cx - 70} 282 c-9-8-7-18 0-26 c0 7 4 9 6 9 c-2-8 2-15 8-19 c-1 9 9 12 9 22 c0 9-7 14-12 14 c-5 0-9-2-11-0z"
            fill="url(#flame)" filter="url(#glow)">
        <animateTransform attributeName="transform" type="scale" values="1 1;1 1.06;1 1" dur="1.4s"
                          additive="sum" repeatCount="indefinite"/>
      </path>"""
        big.append(f"""
    <g opacity="0">
      <animate attributeName="opacity" values="0;1" dur=".5s" begin="{0.6 + i * 0.15:.2f}s" fill="freeze"/>{flame}
      <text x="{cx}" y="282" text-anchor="middle" class="big" filter="url(#glow)">{fmt(n)}</text>
      <text x="{cx}" y="302" text-anchor="middle" class="unit">{esc(unit)}</text>
      <text x="{cx}" y="324" text-anchor="middle" class="cap">{esc(cap)}</text>
    </g>""")

    body = f"""  <defs>
    <clipPath id="frame"><rect width="{w}" height="{h}" rx="16"/></clipPath>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG2}"/>
    </linearGradient>
    <radialGradient id="ember" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{ACCENT}" stop-opacity=".35"/>
      <stop offset="100%" stop-color="#000" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#6d28d9"/><stop offset="1" stop-color="{HOT}"/>
    </linearGradient>
    <linearGradient id="split" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/>
      <stop offset=".5" stop-color="{ACCENT}" stop-opacity=".45"/>
      <stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="flame" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0" stop-color="{ACCENT}"/><stop offset="1" stop-color="{HOT}"/>
    </linearGradient>{glow()}
  </defs>
  <style>
    text  {{ font-family: {FONT}; }}
    .h    {{ fill: #ffffff; font-size: 15px; font-weight: bold; letter-spacing: 2.4px; }}
    .lbl  {{ fill: {DESC}; font-size: 13px; }}
    .num  {{ fill: #ffffff; font-size: 15px; font-weight: bold; }}
    .pct  {{ fill: {SOFT}; font-size: 12px; }}
    .big  {{ fill: #ffffff; font-size: 30px; font-weight: bold; }}
    .unit {{ fill: {SOFT}; font-size: 11px; }}
    .cap  {{ fill: {DESC}; font-size: 11px; font-weight: bold; letter-spacing: 1.6px; }}
  </style>
  <g clip-path="url(#frame)">
    <rect width="{w}" height="{h}" fill="url(#bg)"/>
    <ellipse cx="200" cy="140" rx="260" ry="150" fill="url(#ember)">
      <animate attributeName="opacity" values=".5;1;.5" dur="3.4s" repeatCount="indefinite"/>
    </ellipse>
    <ellipse cx="680" cy="140" rx="260" ry="150" fill="url(#ember)" opacity=".6">
      <animate attributeName="opacity" values="1;.5;1" dur="3.4s" repeatCount="indefinite"/>
    </ellipse>
    <g filter="url(#glow)">
      <text x="40" y="48" class="h">ACTIVIDAD</text>
      <text x="490" y="48" class="h">LENGUAJES</text>
    </g>
    <rect x="40" y="60" width="0" height="2" fill="{ACCENT}">
      <animate attributeName="width" values="0;370;370;0" keyTimes="0;.35;.8;1" dur="6s" repeatCount="indefinite"/>
    </rect>
    <rect x="490" y="60" width="0" height="2" fill="{ACCENT}">
      <animate attributeName="width" values="0;370;370;0" keyTimes="0;.35;.8;1" dur="6s" begin="-3s" repeatCount="indefinite"/>
    </rect>
    <rect x="449.5" y="40" width="1" height="170" fill="{ACCENT}" opacity=".25"/>{''.join(act)}{''.join(langs)}
    <rect x="40" y="232" width="820" height="1" fill="url(#split)"/>{''.join(big)}
    <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="15" fill="none" stroke="{DIM2}" stroke-width="1.5">{BORDER_SURGE}</rect>
    {running_light(1, 1, w - 2, h - 2, 15, dash=6, dur="12s")}
  </g>"""
    return svg(w, h, "Estadísticas de GitHub", body)


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    who, out = sys.argv[1], sys.argv[2]
    data = SAMPLE if who == "--sample" else summarize(fetch(who))
    with open(out, "w", encoding="utf-8") as f:
        f.write(render(data))
    print(f"✓ {out}")


if __name__ == "__main__":
    main()
