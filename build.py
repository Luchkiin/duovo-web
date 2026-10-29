"""Builds the site from one template per page, so Swedish and English stay in step.

    python3 build.py            draft of every page in preview/ (local only, never published; privacy and
                                support need drafts/pages.py, which is gitignored and never in the repo):
                                undecided parts are highlighted and a draft banner is shown
    python3 build.py --release  the pages in RELEASE_PAGES only, in docs/ (what GitHub Pages publishes),
                                without draft banner or links to unreleased pages; refuses to build while
                                any of those pages has an undecided part. Writes release-files.txt.
"""
import hashlib, html, pathlib, re, shutil, sys

# Paths relative to this file, so the build works wherever the folder lives.
ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "source"     # Figma exports copied from References/Figma (see source/README.md)
ASSETS = ROOT / "assets"  # CSS, fonts and email logos, copied into the built site
RELEASE = "--release" in sys.argv
OUT = ROOT / ("docs" if RELEASE else "preview")
MANIFEST = ROOT / "release-files.txt"

# The pages in the first public version. Privacy and support stay drafts until their basis is decided.
RELEASE_PAGES = ("home",)
BUILT_PAGES = RELEASE_PAGES if RELEASE else ("home", "privacy", "support")


def svg_current(path, cls=None):
    s = path.read_text()
    s = s.replace('"black"', '"currentColor"')
    s = re.sub(r'\s(width|height)="[^"]*"', "", s, count=2)
    attrs = ' aria-hidden="true" focusable="false"' + (f' class="{cls}"' if cls else "")
    return s.replace("<svg", "<svg" + attrs, 1).strip()


def icon(name):
    return svg_current(SRC / "icons" / f"{name}.svg")


LOGO = svg_current(SRC / "logos/logotype-large-light.svg")
SYMBOL = svg_current(SRC / "logos/symbol-small-light.svg", "symbol")
TICK = '<svg aria-hidden="true" focusable="false" viewBox="0 0 12 12"><path d="M2.5 6.5 L4.8 8.8 L9.5 3.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'

# Pages per language: key -> path below the site root. The language switch links each page to its counterpart.
PATHS = {
    "sv": {"home": "", "privacy": "integritet/", "support": "support/"},
    "en": {"home": "en/", "privacy": "en/privacy/", "support": "en/support/"},
}

UI = {
    "sv": dict(other_label="English", privacy="Integritet", support="Support",
               coming="Sidor om integritet och support kommer.",
               draft="Utkast – inte publicerat. Gula markeringar saknar beslut eller verifiering och ska åtgärdas före publicering.",
               launch="Anpassas till den version som lanseras", verify="Avsedd funktion – verifieras före publicering"),
    "en": dict(other_label="Svenska", privacy="Privacy", support="Support",
               coming="Pages on privacy and support are on their way.",
               draft="Draft – not published. Yellow highlights lack a decision or verification and must be resolved before publishing.",
               launch="Adjust to the version that is released", verify="Intended behaviour – verify before publishing"),
}

CONTACT = "hej@duovo.app"  # decided 2026-10-29; forwarding verified with a delivery test (planning/Kontaktadress.md)
CONTACT_LINK = f'<a href="mailto:{CONTACT}">{CONTACT}</a>'

# ── Start page ─────────────────────────────────────────────────────────────

HOME = {
    "sv": dict(
        title="Duovo – listor för vardagen",
        description="Duovo är en listapp för inköp och packning. Appen är under utveckling.",
        status="Under utveckling",
        h1='Lite mer <span class="serif">ordning</span> i vardagen.',
        lede="Duovo samlar inköp och packning i listor som är snabba att skriva och sköna att bocka av. Lugnt, snabbt och utan tjafs.",
        note="Duovo finns inte att ladda ner ännu.",
        cards_label="Exempel på två listor i Duovo: en inköpslista där två av fem varor är klara och en packlista med uppsättningen Kläder.",
        g_title="Lördagshandling", g_sub="5 varor",
        g_items=[("Mjölk", True), ("Bröd", True), ("Kaffe", False), ("Bananer", False), ("Ägg", False)],
        g_progress="<strong>2</strong> av 5 klara",
        p_title="Stughelg", p_sub="3 saker", p_section="Kläder",
        p_items=[("Ylletröja", True), ("Regnjacka", False), ("Yllesockor", False)],
        p_added="Kläder tillagd", p_chips=["Hygien", "Utomhus", "Teknik"],
        f_heading='Två sorters listor, <span class="serif">gjorda</span> för vardagen.',
        features=[
            ("Grocery", "tile--sage", "Inköpslistor",
             "Skriv upp det som behövs och bocka av i butiken. Du ser hela tiden hur mycket som är kvar."),
            ("Packing", "tile--clay", "Packlistor",
             "Börja från färdiga uppsättningar för kläder, hygien, utomhus och teknik. Sakerna hamnar i sektioner, och där kan du lägga till, byta namn på och ta bort saker."),
            ("Undo", "tile--ink", "Ångra direkt",
             "Byt namn på en sak eller ta bort den när du vill. Blev det fel? Tryck på Ångra så är den tillbaka."),
        ],
        s_heading='Duovo är under <span class="serif">utveckling.</span>',
        s_body="Appen byggs och testas just nu. Det finns ingen nedladdning ännu, och den här sidan uppdateras när det finns något att prova.",
    ),
    "en": dict(
        title="Duovo – lists for everyday life",
        description="Duovo is a list app for groceries and packing. The app is in development.",
        status="In development",
        h1='A little more <span class="serif">order</span> in everyday life.',
        lede="Duovo keeps groceries and packing in lists that are quick to write and satisfying to tick off. Calm, fast, no clutter.",
        note="Duovo isn't available to download yet.",
        cards_label="Two example lists in Duovo: a grocery list with two of five items done, and a packing list with the Clothing set.",
        g_title="Saturday shop", g_sub="5 items",
        g_items=[("Milk", True), ("Bread", True), ("Coffee", False), ("Bananas", False), ("Eggs", False)],
        g_progress="<strong>2</strong> of 5 done",
        p_title="Cabin weekend", p_sub="3 items", p_section="Clothing",
        p_items=[("Wool sweater", True), ("Rain jacket", False), ("Wool socks", False)],
        p_added="Clothing added", p_chips=["Toiletries", "Outdoor", "Tech"],
        f_heading='Two kinds of lists, <span class="serif">made</span> for everyday life.',
        features=[
            ("Grocery", "tile--sage", "Grocery lists",
             "Write down what you need and tick it off in the shop. You always see how much is left."),
            ("Packing", "tile--clay", "Packing lists",
             "Start from ready-made sets for clothing, toiletries, outdoor and tech. Items land in sections, where you can add, rename and remove items."),
            ("Undo", "tile--ink", "Undo right away",
             "Rename an item or delete it whenever you like. Made a mistake? Tap Undo and it's back."),
        ],
        s_heading='Duovo is in <span class="serif">development.</span>',
        s_body="The app is being built and tested right now. There's no download yet, and this page will be updated when there's something to try.",
    ),
}

# ── Privacy and support drafts ─────────────────────────────────────────────
# The draft texts live in drafts/pages.py, which is excluded in .gitignore so they never
# reach the public repository. Drafts build them when the file exists; --release never needs them.

def load_drafts():
    path = ROOT / "drafts" / "pages.py"
    if not path.exists():
        return None
    import importlib.util
    spec = importlib.util.spec_from_file_location("duovo_drafts", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DRAFTS = None if RELEASE else load_drafts()
if not RELEASE and DRAFTS is None:
    BUILT_PAGES = ("home",)
    print("drafts/pages.py not found: building the start page only")


# ── Rendering ──────────────────────────────────────────────────────────────

TODO = re.compile(r"\[\[(.+?)\]\]")
PASSAGE = re.compile(r"\{\{(launch|verify)\|(.+?)\}\}", re.S)
undecided = []


def todo(text, where):
    lang = where[:2]
    text = text.replace("{contact}", CONTACT_LINK)

    def mark(m):
        undecided.append(f"{where}: {m.group(1)}")
        return f'<mark class="todo">{html.escape(m.group(1))}</mark>'

    def passage(m):
        kind, inner = m.group(1), m.group(2)
        plain = re.sub(r"<[^>]+>|\[\[|\]\]", "", inner)
        undecided.append(f"{where}: ({kind}) {plain[:60]}…")
        return (f'<span class="cond"><span class="cond-label">{UI[lang][kind]}:</span> '
                f"{TODO.sub(mark, inner)}</span>")

    return TODO.sub(mark, PASSAGE.sub(passage, text))


def rel(lang, key):
    """Relative prefix from a page back to the site root."""
    return "../" * PATHS[lang][key].count("/")


def link(from_lang, from_key, to_lang, to_key):
    return rel(from_lang, from_key) + PATHS[to_lang][to_key] or "./"


def layout(lang, key, title, description, body):
    other = "en" if lang == "sv" else "sv"
    root = rel(lang, key)
    u = UI[lang]
    banner = "" if RELEASE else f'<div class="draft-banner" role="note">{u["draft"]}</div>\n  '
    switch = link(lang, key, other, key)
    nav = lambda k, label: (f'<a href="{link(lang, key, lang, k)}"' + (' aria-current="page"' if k == key else "") + f">{label}</a>")
    # Link only to pages this build contains; otherwise say they are on their way.
    if "privacy" in BUILT_PAGES:
        footer_middle = f'<nav class="footer-nav" aria-label="Duovo">{nav("privacy", u["privacy"])}{nav("support", u["support"])}</nav>'
    else:
        footer_middle = f'<p>{u["coming"]}</p>'
    return f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <meta name="theme-color" content="#F4F1EB" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#13120E" media="(prefers-color-scheme: dark)">
  <link rel="alternate" hreflang="sv" href="https://duovo.app/{PATHS['sv'][key]}">
  <link rel="alternate" hreflang="en" href="https://duovo.app/{PATHS['en'][key]}">
  <link rel="icon" href="{root}assets/img/icon.svg" type="image/svg+xml">
  <link rel="preload" href="{root}assets/fonts/Onest-Variable.ttf" as="font" type="font/ttf" crossorigin>
  <link rel="stylesheet" href="{root}assets/site.css">
</head>
<body>
  {banner}<header class="site-header">
    <div class="wrap">
      <a class="logo" href="{link(lang, key, lang, 'home')}" aria-label="Duovo">{LOGO}</a>
      <a class="lang" href="{switch}" hreflang="{other}" lang="{other}">{u['other_label']}</a>
    </div>
  </header>

  <main>
{body}
  </main>

  <footer class="site-footer">
    <div class="wrap">
      <div class="footer-brand">{SYMBOL}<p>© 2026 Duovo</p></div>
      {footer_middle}
      <a class="lang" href="{switch}" hreflang="{other}" lang="{other}">{u['other_label']}</a>
    </div>
  </footer>
</body>
</html>
"""


def items(rows):
    out = []
    for name, done in rows:
        cls = ' class="is-done"' if done else ""
        tick = TICK if done else ""
        out.append(f'<li{cls}><span class="box">{tick}</span><span class="label">{name}</span></li>')
    return "\n              ".join(out)


def home(lang):
    t = HOME[lang]
    feats = "\n".join(
        f"""        <li class="feature">
          <span class="tile {cls}">{icon(ic)}</span>
          <h3>{h}</h3>
          <p>{p}</p>
        </li>""" for ic, cls, h, p in t["features"])
    chips = "\n              ".join(f'<span class="chip">{icon("Plus")}{c}</span>' for c in t["p_chips"])
    body = f"""    <section class="hero" aria-labelledby="hero-title">
      <div class="wrap">
        <div>
          <p class="status">{t['status']}</p>
          <h1 id="hero-title">{t['h1']}</h1>
          <p class="lede">{t['lede']}</p>
          <p class="note">{t['note']}</p>
        </div>

        <figure class="cards" role="img" aria-label="{t['cards_label']}">
          <div class="card card--grocery" aria-hidden="true">
            <div class="card-head">
              <span class="tile tile--sage">{icon('Grocery')}</span>
              <div><div class="card-title">{t['g_title']}</div><div class="card-sub">{t['g_sub']}</div></div>
            </div>
            <ul class="items">
              {items(t['g_items'])}
            </ul>
            <div class="progress">
              <div class="progress-bar"><span style="width: 40%"></span></div>
              <div class="progress-text">{t['g_progress']}</div>
            </div>
          </div>
          <div class="card card--packing" aria-hidden="true">
            <div class="card-head">
              <span class="tile tile--clay">{icon('Packing')}</span>
              <div><div class="card-title">{t['p_title']}</div><div class="card-sub">{t['p_sub']}</div></div>
            </div>
            <div class="section-label">{t['p_section']}</div>
            <ul class="items">
              {items(t['p_items'])}
            </ul>
            <div class="chips">
              <span class="chip chip--added">{icon('Check')}{t['p_added']}</span>
              {chips}
            </div>
          </div>
        </figure>
      </div>
    </section>

    <section class="features" aria-labelledby="features-title">
      <div class="wrap">
        <h2 id="features-title">{t['f_heading']}</h2>
        <ul class="feature-grid">
{feats}
        </ul>
      </div>
    </section>

    <section class="status-block" aria-labelledby="status-title">
      <div class="wrap">
        <div class="status-card">
          <h2 id="status-title">{t['s_heading']}</h2>
          <p>{t['s_body']}</p>
        </div>
      </div>
    </section>"""
    return layout(lang, "home", t["title"], t["description"], body)


def privacy(lang):
    t = DRAFTS.PRIVACY[lang]
    where = f"{lang}/privacy"
    secs = "\n".join(
        f"""        <section>
          <h2>{h}</h2>
          {todo(b, where)}
        </section>""" for h, b in t["sections"])
    body = f"""    <article class="prose">
      <div class="wrap">
        <h1>{t['h1']}</h1>
        <p class="lede">{t['lede']}</p>
{secs}
        <p class="updated">{todo(t['updated'], where)}</p>
      </div>
    </article>"""
    return layout(lang, "privacy", t["title"], t["description"], body)


def support(lang):
    t = DRAFTS.SUPPORT[lang]
    where = f"{lang}/support"
    privacy_link = link(lang, "support", lang, "privacy")
    faq = "\n".join(
        f"""          <div class="faq-item">
            <h3>{q}</h3>
            <p>{a.format(privacy=privacy_link)}</p>
          </div>""" for q, a in t["faq"])
    body = f"""    <article class="prose">
      <div class="wrap">
        <h1>{t['h1']}</h1>
        <p class="lede">{t['lede']}</p>
        <section class="contact-card">
          <h2>{t['contact_heading']}</h2>
          <p>{todo(t['contact'], where)}</p>
        </section>
        <section>
          <h2>{t['faq_heading']}</h2>
{faq}
        </section>
      </div>
    </article>"""
    return layout(lang, "support", t["title"], t["description"], body)


RENDER = {"home": home, "privacy": privacy, "support": support}
pages = {}
for lang in ("sv", "en"):
    for key in BUILT_PAGES:
        pages[PATHS[lang][key]] = RENDER[key](lang)

if RELEASE and undecided:
    print("Not built: undecided parts remain in release pages:\n  " + "\n  ".join(undecided))
    sys.exit(1)

# Start from an empty output folder so nothing from an earlier build is left behind.
# docs/ keeps only its Pages settings files (.nojekyll, and CNAME once a domain is set).
KEEP = {".nojekyll", "CNAME"}
OUT.mkdir(exist_ok=True)
for item in OUT.iterdir():
    if item.name in KEEP:
        continue
    shutil.rmtree(item) if item.is_dir() else item.unlink()

for path, text in pages.items():
    target = OUT / path / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
shutil.copytree(ASSETS, OUT / "assets", ignore=shutil.ignore_patterns(".DS_Store"))
(OUT / "assets/img").mkdir(exist_ok=True)
shutil.copy(SRC / "logos/app-icon-small-light.svg", OUT / "assets/img/icon.svg")

if RELEASE:
    files = sorted(p for p in OUT.rglob("*") if p.is_file())
    lines = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.stat().st_size:>7}  {p.relative_to(OUT)}" for p in files]
    MANIFEST.write_text("# Files in docs/ that GitHub Pages would publish (sha256, bytes, path). Written by build.py --release.\n"
                        + "\n".join(lines) + "\n")
    print(f"Release: {len(pages)} pages, {len(files)} files in docs/, listed in {MANIFEST.name}")
else:
    print(f"Draft: {len(pages)} pages in preview/ (local only), {len(undecided)} undecided parts")
