#!/usr/bin/env python3
"""Genera los SVG animados del perfil en assets/.

Uso:  python3 scripts/build_assets.py
Para cambiar textos, proyectos o colores edita las constantes de abajo
y vuelve a ejecutar el script.
"""
import base64
import html
import pathlib
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
USER = "4NDR3S-01"

# ── paleta ──────────────────────────────────────────────────────────────
ACCENT = "#a855f7"      # violeta principal
BRIGHT = "#c084fc"      # violeta claro (bordes, flechas)
SOFT = "#d8b4fe"        # chips / porcentajes
HOT = "#22d3ee"         # acento secundario (cian)
WHITE_HOT = "#f5ecff"   # núcleo de los destellos
DESC = "#cbbfdc"        # texto secundario
DIM = "#3b1a5a"         # bordes apagados
DIM2 = "#5b2a8a"        # borde que se ilumina
BG1, BG2 = "#12081f", "#05020a"
CHIP_BG, CHIP_STROKE = "#1a0b2b", "#4c1d95"
LIGHT_TEXT, LIGHT_ACCENT = "#1e1030", "#7c3aed"

FONT = "Verdana,DejaVu Sans,sans-serif"
MONO = "'JetBrains Mono','DejaVu Sans Mono',Consolas,monospace"

NAME = "ANDRÉS CABRERA"

TYPING = [
    "Full Stack Developer · Next.js + TypeScript",
    "Mobile · React Native + Expo + Kotlin",
    "Backend · NestJS + Prisma + PostgreSQL",
    "IA aplicada · apps que ayudan a aprender",
    "Ciberseguridad · redes · Linux",
    "Siempre aprendiendo, siempre construyendo",
]

PROJECTS = [
    dict(slug="medicai", name="MedicAI", tag="TESIS",
         desc="Asistente inteligente de medicación: app móvil, plataforma web y API en un monorepo con notificaciones y geolocalización.",
         chips=["Expo", "React Native", "Next.js", "NestJS", "Prisma"]),
    dict(slug="apuntequiz", name="ApunteQuiz", tag="IA",
         desc="Convierte apuntes en PDF o texto en resúmenes y quizzes generados con IA. Incluye OCR, accesibilidad y dashboard.",
         chips=["Next.js", "Gemini AI", "Supabase", "Tesseract", "Zod"]),
    dict(slug="psicoreto", name="PsicoReto", tag="EDTECH",
         desc="Plataforma de estudio de psicopatología con casos clínicos, retos, modo examen, repaso espaciado y gamificación.",
         chips=["Next.js 16", "React 19", "Tailwind 4", "Supabase"]),
    dict(slug="titulacion", name="Titulación", tag="FULL STACK",
         desc="Sistema web para gestionar procesos de titulación universitaria, con autenticación, roles y base de datos relacional.",
         chips=["Next.js", "NextAuth", "PostgreSQL", "Zod"]),
]

# ids de skillicons.dev; "devicon:<ruta>" o "si:<nombre>" (Simple Icons) para los que
# skillicons no tiene, y "custom:<clave>" para los dibujados a mano en CUSTOM_ICONS
STACK = [
    ("FRONTEND", ["ts", "js", "react", "nextjs", "angular", "vue", "tailwind", "bootstrap", "html", "css"]),
    ("MOBILE", ["react", "kotlin", "flutter", "swift", "androidstudio"]),
    ("BACKEND", ["nodejs", "nestjs", "php", "laravel", "py", "django", "java", "cs", "cpp"]),
    ("DATA", ["postgres", "mysql", "devicon:mariadb/mariadb-original", "mongodb",
              "devicon:couchdb/couchdb-original", "firebase", "prisma"]),
    ("DEVOPS", ["docker", "git", "github", "githubactions", "linux", "vercel", "figma", "arduino", "unity"]),
    ("SECURITY", ["si:kalilinux", "si:wireshark", "custom:nmap", "custom:tcpdump", "si:cisco",
                  "si:burpsuite", "si:zap", "custom:sqlmap", "si:metasploit", "custom:hydra",
                  "custom:john", "custom:aircrack"]),
]

TITLES = {
    "about": "SOBRE MÍ",
    "projects": "PROYECTOS",
    "stack": "TECNOLOGÍAS",
    "stats": "ESTADÍSTICAS",
    "contact": "CONTACTO",
}

BUTTONS = ["portfolio", "linkedin", "email", "whatsapp", "telegram",
           "instagram", "discord", "x", "facebook"]


# ── utilidades ──────────────────────────────────────────────────────────
def esc(s):
    return html.escape(s, quote=True)


def fetch(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "profile-builder"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.read()
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(1.5)


def shine(gid, width, dark="#ffffff", band=BRIGHT, x1=-300, span=260, dur="4.5s"):
    return f"""
    <linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x1}" y1="0" x2="{x1 + span}" y2="0">
      <stop offset="0"    stop-color="{dark}"/>
      <stop offset="0.42" stop-color="{dark}"/>
      <stop offset="0.5"  stop-color="{band}"/>
      <stop offset="0.58" stop-color="{dark}"/>
      <stop offset="1"    stop-color="{dark}"/>
      <animate attributeName="x1" from="{x1}" to="{width}" dur="{dur}" repeatCount="indefinite"/>
      <animate attributeName="x2" from="{x1 + span}" to="{width + span}" dur="{dur}" repeatCount="indefinite"/>
    </linearGradient>"""


def glow(fid="glow", std=2.6):
    return f"""
    <filter id="{fid}" x="-25%" y="-60%" width="150%" height="220%">
      <feGaussianBlur stdDeviation="{std}" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>"""


def soft(fid="soft", std=7):
    return f"""
    <filter id="{fid}" x="-40%" y="-100%" width="180%" height="320%">
      <feGaussianBlur stdDeviation="{std}"/>
    </filter>"""


SURGE = 'values="0;.85;.1;0;0" keyTimes="0;.012;.06;.13;1" dur="12s" repeatCount="indefinite"'
BORDER_SURGE = (f'<animate attributeName="stroke" values="{DIM2};{BRIGHT};{DIM2};{DIM2}" '
                f'keyTimes="0;.015;.12;1" dur="12s" repeatCount="indefinite"/>')


def running_light(x, y, w, h, rx, dash=12, dur="6s", reverse=False, width=2):
    to = "100" if reverse else "-100"
    return f"""
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="none" stroke="{BRIGHT}"
        stroke-width="{width}" pathLength="100" stroke-dasharray="{dash} {100 - dash}" stroke-linecap="round"
        filter="url(#glow)">
    <animate attributeName="stroke-dashoffset" from="0" to="{to}" dur="{dur}" repeatCount="indefinite"/>
  </rect>"""


def arrow(x, y, size=5):
    return f"""
  <path d="M{x} {y} l{size} {size} l-{size} {size}" fill="none" stroke="{BRIGHT}" stroke-width="2.2"
        stroke-linecap="round" stroke-linejoin="round">
    <animateTransform attributeName="transform" type="translate" values="0,0; 4,0; 0,0" dur="1.6s"
                      calcMode="spline" keyTimes="0;0.5;1" keySplines=".45 0 .55 1;.45 0 .55 1"
                      repeatCount="indefinite"/>
  </path>"""


def svg(w, h, label, body, extra_ns=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg"{extra_ns} viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" role="img" aria-label="{esc(label)}">\n'
            f'  <title>{esc(label)}</title>\n{body}\n</svg>\n')


def write(name, content):
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"  ✓ assets/{name}  ({len(content.encode()) // 1024} KB)")


def text_width(s, size, bold=True):
    """Ancho aproximado de un texto en Verdana."""
    per = 0.68 if bold else 0.62
    return sum(size * (0.33 if c == " " else per) for c in s)


# ── nombre ──────────────────────────────────────────────────────────────
def build_name():
    w, h = 640, 104
    t = esc(NAME)
    common = f'x="{w / 2}" y="58" text-anchor="middle" font-family="{FONT}" font-size="42" font-weight="bold" letter-spacing="3"'
    uw = 400
    body = f"""  <defs>{shine("shine", w)}{shine("shineLight", w, dark=LIGHT_TEXT, band=LIGHT_ACCENT)}{soft()}
  </defs>
  <style>
    .t {{ fill: url(#shine); }}
    @media (prefers-color-scheme: light) {{ .t {{ fill: url(#shineLight); }} }}
  </style>
  <g>
    <animateTransform attributeName="transform" type="translate" values="0,0; 0,-3.5; 0,0" dur="5.5s"
                      calcMode="spline" keyTimes="0;0.5;1" keySplines=".45 0 .55 1;.45 0 .55 1" repeatCount="indefinite"/>
    <text {common} filter="url(#soft)" fill="{ACCENT}" opacity=".45">{t}
      <animate attributeName="opacity" values=".28;.7;.28" dur="3.4s" repeatCount="indefinite"/>
    </text>
    <text {common} class="t">{t}</text>
    <text {common} filter="url(#soft)" fill="{HOT}" opacity="0">{t}
      <animate attributeName="opacity" {SURGE}/>
    </text>
    <rect x="{w / 2}" y="76" width="0" height="2" fill="{ACCENT}">
      <animate attributeName="width" values="0;{uw};{uw};0" keyTimes="0;.35;.8;1" dur="6s" repeatCount="indefinite"/>
      <animate attributeName="x" values="{w / 2};{w / 2 - uw / 2};{w / 2 - uw / 2};{w / 2}" keyTimes="0;.35;.8;1" dur="6s" repeatCount="indefinite"/>
    </rect>
  </g>"""
    write("name.svg", svg(w, h, NAME.title(), body))


# ── banner ──────────────────────────────────────────────────────────────
def build_banner():
    w, h = 1000, 320
    raw = fetch(f"https://github.com/{USER}.png?size=360")
    mime = "image/png" if raw[:4] == b"\x89PNG" else "image/jpeg"
    avatar = base64.b64encode(raw).decode()
    cx, cy, r = 205, 160, 92

    # partículas que suben
    import random
    random.seed(7)
    particles = []
    for i in range(26):
        x = random.randint(20, 980)
        rr = random.choice([1, 1.2, 1.5, 2])
        dur = random.uniform(7, 14)
        begin = -random.uniform(0, 14)
        col = random.choice([ACCENT, BRIGHT, HOT, BRIGHT])
        particles.append(
            f'<circle cx="{x}" cy="330" r="{rr}" fill="{col}">'
            f'<animate attributeName="cy" values="330;-10" dur="{dur:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;.9;.6;0" keyTimes="0;.2;.7;1" dur="{dur:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite"/>'
            f'</circle>')

    # tarjeta de código
    code_x, code_y = 420, 196
    code = [
        [("const ", "#c084fc"), ("andres", "#f5ecff"), (" = {", "#cbbfdc")],
        [("  stack: ", "#cbbfdc"), ('"full-stack"', "#86efac"), (",", "#cbbfdc")],
        [("  focus: [", "#cbbfdc"), ('"web"', "#86efac"), (", ", "#cbbfdc"), ('"mobile"', "#86efac"),
         (", ", "#cbbfdc"), ('"IA"', "#86efac"), ("],", "#cbbfdc")],
        [("  learning: ", "#cbbfdc"), ("true", HOT), (" };", "#cbbfdc")],
    ]
    code_lines = []
    for i, parts in enumerate(code):
        spans = "".join(f'<tspan fill="{c}">{esc(t)}</tspan>' for t, c in parts)
        b = 0.35 + i * 0.25
        code_lines.append(
            f'<text x="{code_x + 18}" y="{code_y + 42 + i * 19}" class="code" opacity="0">{spans}'
            f'<animate attributeName="opacity" values="0;1" dur=".4s" begin="{b:.2f}s" fill="freeze"/></text>')

    body = f"""  <defs>
    <clipPath id="frame"><rect width="{w}" height="{h}" rx="16"/></clipPath>
    <clipPath id="avatar"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG2}"/>
    </linearGradient>
    <radialGradient id="ember" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{ACCENT}" stop-opacity=".55"/>
      <stop offset="45%" stop-color="#6d28d9" stop-opacity=".22"/>
      <stop offset="100%" stop-color="#000" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="ember2" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{HOT}" stop-opacity=".22"/>
      <stop offset="100%" stop-color="#000" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="vignette" cx="50%" cy="50%" r="72%">
      <stop offset="55%" stop-color="#000" stop-opacity="0"/>
      <stop offset="100%" stop-color="#000" stop-opacity=".75"/>
    </radialGradient>
    <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{HOT}"/><stop offset=".5" stop-color="{ACCENT}"/><stop offset="1" stop-color="#6d28d9"/>
    </linearGradient>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M32 0H0V32" fill="none" stroke="{ACCENT}" stroke-opacity=".07"/>
    </pattern>{shine("titleShine", w, x1=150, span=260, dur="5.2s")}{glow()}{soft("soft", 9)}
  </defs>
  <style>
    text {{ font-family: {FONT}; }}
    .hi    {{ fill: {HOT}; font-size: 14px; font-weight: bold; letter-spacing: 4px; }}
    .title {{ font-size: 44px; font-weight: bold; letter-spacing: 2px; }}
    .sub   {{ fill: {DESC}; font-size: 16px; letter-spacing: 1px; }}
    .code  {{ font-family: {MONO}; font-size: 13.5px; }}
  </style>
  <g clip-path="url(#frame)">
    <rect width="{w}" height="{h}" fill="url(#bg)"/>
    <rect width="{w}" height="{h}" fill="url(#grid)">
      <animate attributeName="y" values="0;32" dur="4s" repeatCount="indefinite"/>
    </rect>
    <ellipse cx="{cx}" cy="{cy}" rx="300" ry="230" fill="url(#ember)">
      <animate attributeName="opacity" values=".55;1;.55" dur="3.4s" repeatCount="indefinite"/>
    </ellipse>
    <ellipse cx="880" cy="40" rx="320" ry="200" fill="url(#ember2)">
      <animate attributeName="opacity" values="1;.4;1" dur="5s" repeatCount="indefinite"/>
    </ellipse>
    {''.join(particles)}

    <!-- avatar flotando -->
    <g>
      <animateTransform attributeName="transform" type="translate" values="0,0; 0,-6; 0,0" dur="5.5s"
                        calcMode="spline" keyTimes="0;0.5;1" keySplines=".45 0 .55 1;.45 0 .55 1" repeatCount="indefinite"/>
      <circle cx="{cx}" cy="{cy}" r="{r + 14}" fill="none" stroke="{ACCENT}" stroke-width="10" filter="url(#soft)" opacity=".5">
        <animate attributeName="opacity" values=".3;.75;.3" dur="3.4s" repeatCount="indefinite"/>
      </circle>
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="#1a0b2b"/>
      <image href="data:{mime};base64,{avatar}" x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}"
             clip-path="url(#avatar)" preserveAspectRatio="xMidYMid slice"/>
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="url(#ring)" stroke-width="3"/>
      <g>
        <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="18s" repeatCount="indefinite"/>
        <circle cx="{cx}" cy="{cy}" r="{r + 14}" fill="none" stroke="{BRIGHT}" stroke-width="1.5"
                stroke-dasharray="4 10" opacity=".7"/>
      </g>
      <g filter="url(#glow)">
        <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="-360 {cx} {cy}" dur="9s" repeatCount="indefinite"/>
        <circle cx="{cx + r + 14}" cy="{cy}" r="4.5" fill="{HOT}"/>
      </g>
      <g filter="url(#glow)">
        <animateTransform attributeName="transform" type="rotate" from="180 {cx} {cy}" to="540 {cx} {cy}" dur="13s" repeatCount="indefinite"/>
        <circle cx="{cx + r + 14}" cy="{cy}" r="3.5" fill="{BRIGHT}"/>
      </g>
    </g>

    <!-- textos -->
    <text x="420" y="76" class="hi">HOLA, SOY</text>
    <text x="420" y="124" class="title" fill="url(#titleShine)" filter="url(#glow)">{esc(NAME)}</text>
    <text x="420" y="124" class="title" fill="{HOT}" filter="url(#soft)" opacity="0">{esc(NAME)}
      <animate attributeName="opacity" {SURGE}/>
    </text>
    <rect x="420" y="140" width="0" height="2.5" fill="{ACCENT}">
      <animate attributeName="width" values="0;360;360;0" keyTimes="0;.35;.8;1" dur="6s" repeatCount="indefinite"/>
    </rect>
    <text x="420" y="172" class="sub">Full Stack Developer · Web &amp; Mobile · Ecuador</text>

    <!-- bloque de código -->
    <rect x="{code_x}" y="{code_y}" width="420" height="104" rx="10" fill="#0b0514" fill-opacity=".85" stroke="{DIM}"/>
    <circle cx="{code_x + 16}" cy="{code_y + 14}" r="4" fill="#f87171"/>
    <circle cx="{code_x + 30}" cy="{code_y + 14}" r="4" fill="#fbbf24"/>
    <circle cx="{code_x + 44}" cy="{code_y + 14}" r="4" fill="#4ade80"/>
    {''.join(code_lines)}
    <rect x="{code_x + 262}" y="{code_y + 85}" width="8" height="15" fill="{BRIGHT}">
      <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1s" repeatCount="indefinite"/>
    </rect>

    <rect width="{w}" height="{h}" fill="url(#vignette)"/>
    <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="15" fill="none" stroke="{DIM2}" stroke-width="1.5">{BORDER_SURGE}</rect>
    {running_light(1, 1, w - 2, h - 2, 15, dash=8, dur="10s")}
  </g>"""
    write("banner.svg", svg(w, h, f"{NAME.title()} - banner animado", body))


# ── texto que se escribe ────────────────────────────────────────────────
def build_typing():
    w, h = 720, 56
    size = 22
    cw = size * 0.6           # ancho de un carácter monoespaciado
    t_type, t_del, hold, gap = 0.075, 0.035, 1.8, 0.35

    # línea de tiempo global
    windows, t = [], 0.0
    for line in TYPING:
        n = len(line)
        start = t
        t += n * t_type + hold + n * t_del + gap
        windows.append((start, n))
    total = t

    clips, texts = [], []
    for i, (line, (start, n)) in enumerate(zip(TYPING, windows)):
        x0 = (w - n * cw) / 2
        times, vals = [0.0], [0]
        if start > 0:
            times.append(start); vals.append(0)
        for k in range(1, n + 1):
            times.append(start + k * t_type); vals.append(k)
        tdel = start + n * t_type + hold
        for k in range(n - 1, -1, -1):
            times.append(tdel + (n - k) * t_del); vals.append(k)
        kt = ";".join(f"{min(x / total, 1):.4f}" for x in times)
        widths = ";".join(f"{v * cw:.1f}" for v in vals)
        cur = ";".join(f"{x0 + v * cw:.1f}" for v in vals)
        clips.append(f"""
    <clipPath id="c{i}"><rect x="{x0:.1f}" y="0" width="0" height="{h}">
      <animate attributeName="width" calcMode="discrete" dur="{total:.2f}s" repeatCount="indefinite" keyTimes="{kt}" values="{widths}"/>
    </rect></clipPath>""")
        vis_end = (tdel + n * t_del) / total
        texts.append(f"""
  <g clip-path="url(#c{i})">
    <text x="{x0:.1f}" y="36" class="ty" filter="url(#glow)">{esc(line)}</text>
  </g>
  <rect x="{x0:.1f}" y="16" width="3" height="26" fill="{HOT}" opacity="0">
    <animate attributeName="x" calcMode="discrete" dur="{total:.2f}s" repeatCount="indefinite" keyTimes="{kt}" values="{cur}"/>
    <animate attributeName="opacity" calcMode="discrete" dur="{total:.2f}s" repeatCount="indefinite"
             keyTimes="0;{start / total:.4f};{vis_end:.4f}" values="0;1;0"/>
  </rect>""")

    body = f"""  <defs>{glow(std=2.2)}{''.join(clips)}
  </defs>
  <style>
    .ty {{ font-family: {MONO}; font-size: {size}px; fill: {BRIGHT}; }}
    @media (prefers-color-scheme: light) {{ .ty {{ fill: {LIGHT_ACCENT}; }} }}
  </style>{''.join(texts)}"""
    write("typing.svg", svg(w, h, " | ".join(TYPING), body))


# ── títulos de sección ──────────────────────────────────────────────────
def build_title(key, label):
    w, h = 560, 60
    tl = round(text_width(label, 26) + 2 * len(label))
    t = esc(label)
    common = f'x="40" y="41" textLength="{tl}" lengthAdjust="spacing" font-family="{FONT}" font-size="26" font-weight="bold"'
    body = f"""  <defs>{shine("shine", w, x1=-300)}{shine("shineLight", w, dark=LIGHT_TEXT, band=LIGHT_ACCENT)}
    <linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{ACCENT}" stop-opacity=".55"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/>
    </linearGradient>{soft(std=6)}
  </defs>
  <style>
    .t {{ fill: url(#shine); }}
    @media (prefers-color-scheme: light) {{ .t {{ fill: url(#shineLight); }} }}
  </style>
  <g transform="translate(16 31) rotate(45)">
    <rect x="-9" y="-9" width="18" height="18" fill="{ACCENT}" filter="url(#soft)">
      <animate attributeName="opacity" values=".35;.9;.35" dur="3.4s" repeatCount="indefinite"/>
    </rect>
    <rect x="-5.5" y="-5.5" width="11" height="11" fill="{BRIGHT}">
      <animateTransform attributeName="transform" type="scale" values="1;1.18;1" dur="3.4s" repeatCount="indefinite"/>
    </rect>
  </g>
  <text {common} filter="url(#soft)" fill="{ACCENT}" opacity=".4">{t}
    <animate attributeName="opacity" values=".22;.6;.22" dur="3.4s" repeatCount="indefinite"/>
  </text>
  <text {common} class="t">{t}</text>
  <text {common} filter="url(#soft)" fill="{HOT}" opacity="0">{t}
    <animate attributeName="opacity" {SURGE}/>
  </text>
  <rect x="40" y="53" width="500" height="1" fill="url(#rule)"/>
  <rect x="40" y="52" width="0" height="2" fill="{BRIGHT}">
    <animate attributeName="width" values="0;{tl};{tl};0" keyTimes="0;.35;.8;1" dur="6s" repeatCount="indefinite"/>
  </rect>"""
    write(f"title-{key}.svg", svg(w, h, label.title(), body))


# ── divisor ─────────────────────────────────────────────────────────────
def build_divider():
    w, h = 1000, 28
    body = f"""  <defs>
    <linearGradient id="base" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/>
      <stop offset=".5" stop-color="{ACCENT}" stop-opacity=".55"/>
      <stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="pulseL" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/>
      <stop offset=".85" stop-color="{BRIGHT}" stop-opacity=".9"/>
      <stop offset="1" stop-color="{WHITE_HOT}"/>
    </linearGradient>
    <linearGradient id="pulseR" x1="1" y1="0" x2="0" y2="0">
      <stop offset="0" stop-color="{HOT}" stop-opacity="0"/>
      <stop offset=".85" stop-color="{HOT}" stop-opacity=".9"/>
      <stop offset="1" stop-color="{WHITE_HOT}"/>
    </linearGradient>
    <filter id="soft" x="-50%" y="-300%" width="200%" height="700%"><feGaussianBlur stdDeviation="4"/></filter>
    <filter id="glow" x="-20%" y="-300%" width="140%" height="700%">
      <feGaussianBlur stdDeviation="2.4" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect x="0" y="13.5" width="1000" height="1" fill="url(#base)"/>
  <g filter="url(#glow)">
    <rect x="-220" y="12.5" width="220" height="3" fill="url(#pulseL)" opacity="0">
      <animate attributeName="x" values="-220;-220;270;270" keyTimes="0;.05;.5;1" calcMode="spline"
               keySplines="0 0 1 1;.5 0 .9 .6;0 0 1 1" dur="6s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.1;.49;.52;1" dur="6s" repeatCount="indefinite"/>
    </rect>
    <rect x="1000" y="12.5" width="220" height="3" fill="url(#pulseR)" opacity="0">
      <animate attributeName="x" values="1000;1000;510;510" keyTimes="0;.05;.5;1" calcMode="spline"
               keySplines="0 0 1 1;.5 0 .9 .6;0 0 1 1" dur="6s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.1;.49;.52;1" dur="6s" repeatCount="indefinite"/>
    </rect>
  </g>
  <rect x="500" y="13" width="0" height="2" fill="{BRIGHT}" opacity="0" filter="url(#glow)">
    <animate attributeName="width" values="0;0;380;380" keyTimes="0;.5;.75;1" dur="6s" repeatCount="indefinite"/>
    <animate attributeName="x" values="500;500;310;310" keyTimes="0;.5;.75;1" dur="6s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0;0;.8;0;0" keyTimes="0;.5;.52;.75;1" dur="6s" repeatCount="indefinite"/>
  </rect>
  <g transform="translate(500 14)">
    <rect x="-10" y="-10" width="20" height="20" fill="{ACCENT}" filter="url(#soft)" transform="rotate(45)" opacity=".3">
      <animate attributeName="opacity" values=".3;.3;1;.3;.3" keyTimes="0;.5;.53;.7;1" dur="6s" repeatCount="indefinite"/>
    </rect>
    <rect x="-8" y="-8" width="16" height="16" fill="none" stroke="{BRIGHT}" stroke-width="1.2" opacity=".75">
      <animateTransform attributeName="transform" type="rotate" from="45" to="405" dur="12s" repeatCount="indefinite"/>
    </rect>
    <rect x="-4" y="-4" width="8" height="8" fill="{BRIGHT}" transform="rotate(45)">
      <animate attributeName="fill" values="{BRIGHT};{BRIGHT};{WHITE_HOT};{BRIGHT};{BRIGHT}" keyTimes="0;.5;.52;.62;1" dur="6s" repeatCount="indefinite"/>
    </rect>
  </g>"""
    write("divider.svg", svg(w, h, "divider", body))


# ── tarjetas de proyecto ────────────────────────────────────────────────
def wrap(s, limit):
    lines, cur = [], ""
    for word in s.split():
        if cur and len(cur) + 1 + len(word) > limit:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    if cur:
        lines.append(cur)
    return lines


def build_project(p):
    w, h = 440, 230
    tag_w = round(len(p["tag"]) * 7.4 + 20)
    desc = "".join(f'\n  <text x="26" y="{92 + i * 20}" class="desc">{esc(l)}</text>'
                   for i, l in enumerate(wrap(p["desc"], 50)[:3]))
    chips, x = [], 26
    for i, c in enumerate(p["chips"]):
        cw_ = round(len(c) * 7.1 + 18)
        if x + cw_ > w - 26:
            break
        dur = 0.75 + i * 0.1
        kt = 0.3 / dur
        chips.append(f"""
    <g>
      <animate attributeName="opacity" values="0;0;1" keyTimes="0;{kt:.3f};1" dur="{dur:.2f}s" fill="freeze"/>
      <rect x="{x}" y="160" width="{cw_}" height="22" rx="11" fill="{CHIP_BG}" stroke="{CHIP_STROKE}"/>
      <text x="{x + cw_ / 2}" y="175" text-anchor="middle" class="chip">{esc(c)}</text>
    </g>""")
        x += cw_ + 6
    uw = min(round(text_width(p["name"], 21)), 300)
    body = f"""  <defs>
    <clipPath id="frame"><rect width="{w}" height="{h}" rx="14"/></clipPath>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG2}"/>
    </linearGradient>
    <radialGradient id="ember" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{ACCENT}" stop-opacity=".4"/>
      <stop offset="100%" stop-color="#000" stop-opacity="0"/>
    </radialGradient>{shine("shine", w, x1=-260, span=200)}{glow()}
  </defs>
  <style>
    text  {{ font-family: {FONT}; }}
    .name {{ font-size: 21px; font-weight: bold; letter-spacing: 1px; }}
    .desc {{ fill: {DESC}; font-size: 12.5px; }}
    .chip {{ fill: {SOFT}; font-size: 11px; }}
    .tag  {{ fill: {HOT}; font-size: 10px; font-weight: bold; letter-spacing: 1px; }}
    .cta  {{ fill: #ece3f7; font-size: 11.5px; font-weight: bold; letter-spacing: 1px; }}
  </style>
  <g clip-path="url(#frame)">
    <rect width="{w}" height="{h}" fill="url(#bg)"/>
    <ellipse cx="{w}" cy="0" rx="240" ry="170" fill="url(#ember)">
      <animate attributeName="opacity" values=".45;1;.45" dur="3.4s" repeatCount="indefinite"/>
    </ellipse>
    <g transform="translate(33 47) rotate(45)">
      <rect x="-5" y="-5" width="10" height="10" fill="{BRIGHT}" filter="url(#glow)">
        <animateTransform attributeName="transform" type="scale" values="1;1.2;1" dur="3.4s" repeatCount="indefinite"/>
      </rect>
    </g>
    <text x="50" y="55" class="name" fill="url(#shine)" filter="url(#glow)">{esc(p["name"])}</text>
    <rect x="{w - 24 - tag_w}" y="36" width="{tag_w}" height="20" rx="4" fill="none" stroke="{HOT}" stroke-opacity=".6"/>
    <text x="{w - 24 - tag_w / 2}" y="50" text-anchor="middle" class="tag">{esc(p["tag"])}</text>
    <rect x="26" y="68" width="0" height="2" fill="{ACCENT}">
      <animate attributeName="width" values="0;{uw};{uw};0" keyTimes="0;.35;.8;1" dur="6s" repeatCount="indefinite"/>
    </rect>{desc}{''.join(chips)}
    <text x="396" y="210" text-anchor="end" class="cta">VER REPO</text>{arrow(404, 201)}
    <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="13" fill="none" stroke="{DIM2}" stroke-width="1.5">{BORDER_SURGE}</rect>
    {running_light(1, 1, w - 2, h - 2, 13)}
  </g>"""
    write(f"project-{p['slug']}.svg", svg(w, h, f"{p['name']} - {p['desc']}", body))


# ── stack ───────────────────────────────────────────────────────────────
ICON_CACHE = ROOT / "scripts" / "icons"
# íconos de devicon demasiado oscuros para el fondo: color original → nuevo
RECOLOR = {"devicon:mariadb/mariadb-original": {"#003545": "#c0765a"}}


# color de marca para los íconos monocromáticos de Simple Icons
SI_COLORS = {"kalilinux": "#3d8bfd", "wireshark": "#1f9ad6", "cisco": "#1ba0d7",
             "burpsuite": "#ff6633", "zap": "#4a9fe0", "metasploit": "#2596cd"}

# íconos propios (viewBox 256): símbolo + nombre debajo
_LBL = '<text x="128" y="222" text-anchor="middle" font-family="Verdana,DejaVu Sans,sans-serif" font-size="38" font-weight="bold" fill="{c}">{t}</text>'
_ST = 'fill="none" stroke="{c}" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"'
CUSTOM_ICONS = {
    # radar
    "nmap": ("#4ade80", "nmap", '<circle cx="128" cy="98" r="62" {st}/><circle cx="128" cy="98" r="28" {st}/>'
                                '<path d="M128 98 L172 54" {st}/><circle cx="150" cy="120" r="9" fill="{c}"/>'),
    # prompt de terminal
    "tcpdump": ("#22d3ee", "tcpdump", '<rect x="52" y="44" width="152" height="112" rx="16" {st}/>'
                                      '<path d="M84 82 l26 20 l-26 20 M124 126 h40" {st}/>'),
    # base de datos con una gota de inyección
    "sqlmap": ("#facc15", "sqlmap", '<ellipse cx="112" cy="58" rx="52" ry="18" {st}/>'
                                    '<path d="M60 58 v80 c0 10 23 18 52 18 s52-8 52-18 v-80 M60 98 c0 10 23 18 52 18 s52-8 52-18" {st}/>'
                                    '<path d="M196 92 c-14 20-14 30-14 36 a14 14 0 0 0 28 0 c0-6 0-16-14-36z" fill="{c}"/>'),
    # tres cabezas
    "hydra": ("#f87171", "hydra", '<path d="M128 160 V96 M128 160 C128 120 84 120 76 72 M128 160 C128 120 172 120 180 72" {st}/>'
                                  '<circle cx="76" cy="62" r="16" fill="{c}"/><circle cx="128" cy="80" r="16" fill="{c}"/>'
                                  '<circle cx="180" cy="62" r="16" fill="{c}"/>'),
    # hash
    "john": ("#c084fc", "hash", '<path d="M104 40 L88 160 M160 40 L144 160 M66 80 H194 M60 122 H188" {st}/>'),
    # wifi
    "aircrack": ("#fb923c", "aircrack", '<path d="M48 88 a114 114 0 0 1 160 0 M76 116 a72 72 0 0 1 104 0 M104 144 a32 32 0 0 1 48 0" {st}/>'
                                        '<circle cx="128" cy="168" r="11" fill="{c}"/>'),
}


def custom_icon(key):
    c, label, glyph = CUSTOM_ICONS[key]
    size = 38 if len(label) <= 5 else 30
    lbl = _LBL.format(c="#e5e7eb", t=label).replace('font-size="38"', f'font-size="{size}"')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 256 256">'
            f'<rect width="256" height="256" rx="60" fill="#242938"/>'
            f'{glyph.format(st=_ST.format(c=c), c=c)}{lbl}</svg>').encode()


def si_icon(raw, name):
    """Ícono de Simple Icons (24x24, una sola ruta) coloreado sobre una baldosa."""
    import re
    d = re.search(r'<path d="([^"]+)"', raw.decode()).group(1)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 256 256">'
            f'<rect width="256" height="256" rx="60" fill="#242938"/>'
            f'<svg x="56" y="56" width="144" height="144" viewBox="0 0 24 24">'
            f'<path fill="{SI_COLORS[name]}" d="{d}"/></svg></svg>').encode()


def icon_svg(ic):
    if ic.startswith("custom:"):
        return custom_icon(ic[7:])
    cached = ICON_CACHE / (ic.replace("devicon:", "").replace("si:", "si_").replace("/", "_") + ".svg")
    if cached.exists():
        return cached.read_bytes()
    data = download_icon(ic)
    ICON_CACHE.mkdir(exist_ok=True)
    cached.write_bytes(data)
    return data


def download_icon(ic):
    if ic.startswith("si:"):
        return si_icon(fetch(f"https://cdn.jsdelivr.net/npm/simple-icons@13.21.0/icons/{ic[3:]}.svg"), ic[3:])
    if not ic.startswith("devicon:"):
        return fetch(f"https://skillicons.dev/icons?i={ic}")
    # ícono de devicon sobre una baldosa con el mismo estilo que skillicons
    raw = fetch(f"https://cdn.jsdelivr.net/gh/devicons/devicon/icons/{ic[8:]}.svg").decode()
    for a, b in RECOLOR.get(ic, {}).items():
        raw = raw.replace(a, b)
    inner = base64.b64encode(raw.encode()).decode()
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 256 256">'
            f'<rect width="256" height="256" rx="60" fill="#242938"/>'
            f'<image x="40" y="40" width="176" height="176" href="data:image/svg+xml;base64,{inner}"/>'
            f'</svg>').encode()


def build_stack():
    w = 900
    row_h, gap, top = 62, 14, 28
    h = top * 2 + len(STACK) * row_h + (len(STACK) - 1) * gap
    cache = {}
    rows = []
    for r, (label, icons) in enumerate(STACK):
        y = top + r * (row_h + gap)
        items = []
        for i, ic in enumerate(icons):
            if ic not in cache:
                cache[ic] = base64.b64encode(icon_svg(ic)).decode()
            dur = 0.5 + i * 0.07 + r * 0.1
            kt = (0.2 + r * 0.1) / dur
            items.append(f"""
      <g>
        <animate attributeName="opacity" values="0;0;1" keyTimes="0;{kt:.3f};1" dur="{dur:.2f}s" fill="freeze"/>
        <animateTransform attributeName="transform" type="translate" values="0 8;0 8;0 0" keyTimes="0;{kt:.3f};1" dur="{dur:.2f}s" fill="freeze"/>
        <image x="{216 + i * 54}" y="{y + 9}" width="44" height="44" href="data:image/svg+xml;base64,{cache[ic]}"/>
      </g>""")
        rows.append(f"""
    <g>
      <rect x="30" y="{y}" width="840" height="{row_h}" rx="12" fill="#0d0617" fill-opacity=".85" stroke="{DIM}"/>
      <rect x="30" y="{y}" width="840" height="{row_h}" rx="12" fill="none" stroke="{BRIGHT}" stroke-width="1.5"
            pathLength="100" stroke-dasharray="8 92" stroke-linecap="round" opacity=".8" filter="url(#glow)">
        <animate attributeName="stroke-dashoffset" from="0" to="-100" dur="9s" begin="-{r * 1.8:.1f}s" repeatCount="indefinite"/>
      </rect>
      <rect x="48" y="{y + 27}" width="8" height="8" fill="{BRIGHT}" transform="rotate(45 52 {y + 31})">
        <animate attributeName="opacity" values=".55;1;.55" dur="3.4s" begin="-{r * 0.6:.1f}s" repeatCount="indefinite"/>
      </rect>
      <text x="72" y="{y + 36}" class="lbl">{esc(label)}</text>{''.join(items)}
    </g>""")
    body = f"""  <defs>
    <clipPath id="frame"><rect width="{w}" height="{h}" rx="16"/></clipPath>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG2}"/>
    </linearGradient>
    <radialGradient id="ember" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{ACCENT}" stop-opacity=".3"/>
      <stop offset="100%" stop-color="#000" stop-opacity="0"/>
    </radialGradient>{glow(std=2.2)}
  </defs>
  <style>
    text {{ font-family: {FONT}; }}
    .lbl {{ fill: #ffffff; font-size: 12.5px; font-weight: bold; letter-spacing: 1.6px; }}
  </style>
  <g clip-path="url(#frame)">
    <rect width="{w}" height="{h}" fill="url(#bg)"/>
    <ellipse cx="{w / 2}" cy="{h / 2}" rx="520" ry="{h * 0.6:.0f}" fill="url(#ember)">
      <animate attributeName="opacity" values=".5;1;.5" dur="3.4s" repeatCount="indefinite"/>
    </ellipse>{''.join(rows)}
    <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="15" fill="none" stroke="{DIM2}" stroke-width="1.5">{BORDER_SURGE}</rect>
  </g>"""
    alt = ". ".join(f"{label}: {', '.join(icons)}" for label, icons in STACK)
    write("stack.svg", svg(w, h, alt, body))


# ── botones de contacto ─────────────────────────────────────────────────
S = f'fill="none" stroke="{BRIGHT}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
ICONS = {
    "portfolio": ("PORTAFOLIO", f'<circle cx="15" cy="13" r="12" {S}/><ellipse cx="15" cy="13" rx="5" ry="12" {S}/>'
                                f'<path d="M3 13h24M5 7h20M5 19h20" {S}/>'),
    "linkedin": ("LINKEDIN", f'<rect x="2" y="0" width="26" height="26" rx="5" {S}/>'
                             f'<path d="M8.5 11v9M8.5 6.5v.5M13.5 20v-9M13.5 15c0-3 1.5-4.2 3.5-4.2s3 1.4 3 4V20" {S}/>'),
    "email": ("EMAIL", f'<rect x="0" y="3" width="30" height="20" rx="3" {S}/><path d="M1.5 5 L15 15 L28.5 5" {S}/>'),
    "whatsapp": ("WHATSAPP", f'<path d="M4 25l2-6a11.5 11.5 0 1 1 4 4z" {S}/>'
                             f'<path d="M11 8.5c-.8 3 3 8 6.5 8.5l2-1.8-2.6-1.6-1.2 1.2c-1.5-.6-3-2.2-3.6-3.6l1.2-1.2-1.6-2.6z" {S}/>'),
    "telegram": ("TELEGRAM", f'<path d="M2 12.5L28 2l-4.5 22-7.5-6.5L12 22v-6.5L24 6 9.5 14.5z" {S}/>'),
    "instagram": ("INSTAGRAM", f'<rect x="2" y="0" width="26" height="26" rx="8" {S}/><circle cx="15" cy="13" r="6" {S}/>'
                               f'<circle cx="22" cy="6" r="1" fill="{BRIGHT}"/>'),
    "discord": ("DISCORD", f'<path d="M6 5c3-1.5 6-2 9-2s6 .5 9 2c2.5 4 3.5 9 3 15-2.5 2-5 3-7 3.5l-1.6-2.8M4 22c-.6-.4-1-.6-1.5-1-.5-6 .5-11 3-15M10 23.5c-2-.5-4-1.2-6-1.5M8 18.5c4.5 2 9.5 2 14 0" {S}/>'
                           f'<circle cx="11" cy="13.5" r="2" fill="{BRIGHT}"/><circle cx="19" cy="13.5" r="2" fill="{BRIGHT}"/>'),
    "x": ("X / TWITTER", f'<path d="M3 1h7l17 24h-7z M27 1L17.5 11.5 M3 25l9.5-10.5" {S}/>'),
    "facebook": ("FACEBOOK", f'<rect x="2" y="0" width="26" height="26" rx="6" {S}/>'
                             f'<path d="M19 6h-2.5c-2 0-3 1.2-3 3V26M10 14h8" {S}/>'),
}


def build_button(key):
    label, icon = ICONS[key]
    w, h = 220, 52
    fs = 14 if len(label) <= 9 else 12.5
    body = f"""  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#170b26"/><stop offset="1" stop-color="#08040e"/>
    </linearGradient>{shine("shine", w, x1=-200, span=140, dur="3.6s")}{glow(std=2.4)}
  </defs>
  <rect x="1" y="1" width="218" height="50" rx="10" fill="url(#bg)"/>
  <rect x="1" y="1" width="218" height="50" rx="10" fill="none" stroke="{DIM2}" stroke-width="1.5">{BORDER_SURGE}</rect>
  {running_light(1, 1, 218, 50, 10, dash=16, dur="3.6s", reverse=True)}
  <g transform="translate(20 13)" filter="url(#glow)">
    <animate attributeName="opacity" values=".75;1;.75" dur="3.4s" repeatCount="indefinite"/>
    {icon}
  </g>
  <text x="62" y="31" font-family="{FONT}" font-size="{fs}" font-weight="bold" letter-spacing="1.6" fill="url(#shine)">{esc(label)}</text>
  {arrow(192, 20, 6)}"""
    write(f"btn-{key}.svg", svg(w, h, label.title(), body))


def main():
    print("Generando assets…")
    build_name()
    build_banner()
    build_typing()
    for k, v in TITLES.items():
        build_title(k, v)
    build_divider()
    for p in PROJECTS:
        build_project(p)
    build_stack()
    for b in BUTTONS:
        build_button(b)


if __name__ == "__main__":
    main()
