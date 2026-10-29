"""Checks the files that would actually become public, independent of how they were built.

    python3 build.py --release && python3 tools/check-public.py

1. docs/ matches release-files.txt exactly: same files, same sizes, same SHA-256 (nothing extra, nothing missing,
   nothing edited after the build). Review release-files.txt: it is the exact list GitHub Pages would publish.
2. Every page in docs/ is free of draft content (banner, highlights, unresolved [[...]] / {{...}}).
3. Every local link and asset reference in docs/ points to a file inside docs/ (no links to unreleased pages).
4. If the folder is a Git repository: every tracked file is on the allow list, and nothing internal
   (preview/, drafts/, planning/, REVIEW.md, the Google profile picture, config, logs) is tracked.
   In a public repository every tracked file is public, including its history.
Exits with 0 only when everything, including tracked files, was checked and passed; 1 if anything fails;
2 if docs/ passed but there is no Git repository, so tracked files were not checked.
"""
import hashlib, pathlib, re, subprocess, sys
from urllib.parse import urlsplit

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
MANIFEST = ROOT / "release-files.txt"
DRAFT_SIGNS = ['class="todo"', 'class="cond"', 'class="draft-banner"', "[[", "{{"]
ALLOWED = ("docs/", "assets/", "source/", "tools/", "build.py", "README.md", ".gitignore", "release-files.txt")
FORBIDDEN = ("preview/", "drafts/", "planning/", "REVIEW.md", "duovo-google-profil", "SupabaseConfig", ".env", ".log", ".xcresult")

failures = []

# 1. docs/ against the manifest
actual = {}
for p in sorted(x for x in DOCS.rglob("*") if x.is_file()):
    actual[str(p.relative_to(DOCS))] = (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_size)
expected = {}
if MANIFEST.exists():
    for line in MANIFEST.read_text().splitlines():
        if line and not line.startswith("#"):
            digest, size, path = line.split(None, 2)
            expected[path] = (digest, int(size))
else:
    failures.append("release-files.txt missing: run python3 build.py --release")
for path in sorted(set(actual) - set(expected)):
    failures.append(f"in docs/ but not in release-files.txt: {path}")
for path in sorted(set(expected) - set(actual)):
    failures.append(f"in release-files.txt but missing from docs/: {path}")
for path in sorted(set(actual) & set(expected)):
    if actual[path] != expected[path]:
        failures.append(f"changed after the release build: {path}")

# 2. draft content and 3. local links
for page in sorted(DOCS.rglob("*.html")):
    text = page.read_text()
    found = [s for s in DRAFT_SIGNS if s in text]
    if found:
        failures.append(f"draft content in docs/{page.relative_to(DOCS)}: {', '.join(found)}")
    for ref in re.findall(r'(?:href|src)="([^"]+)"', text):
        parts = urlsplit(ref)
        if parts.scheme or ref.startswith(("#", "mailto:")):
            continue
        target = (page.parent / parts.path).resolve()
        if target.is_dir():
            target = target / "index.html"
        if not target.is_file() or DOCS.resolve() not in target.parents:
            failures.append(f"broken or outside link in docs/{page.relative_to(DOCS)}: {ref}")

print(f"GitHub Pages would publish {len(actual)} files from docs/ (exact list with SHA-256 in release-files.txt):")
for path, (_, size) in actual.items():
    print(f"  {path}  {size} B")

# 4. tracked files
git = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True)
# Only a repository rooted at this folder counts; a parent repository would list other files.
top = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
in_repo = git.returncode == 0 and pathlib.Path(top.stdout.strip()).resolve() == ROOT.resolve()
if in_repo:
    tracked = [l for l in git.stdout.splitlines() if l]
    print(f"\nTracked in Git (all public in a public repository): {len(tracked)} files")
    for t in tracked:
        if any(x in t for x in FORBIDDEN):
            failures.append(f"internal file tracked: {t}")
        elif not t.startswith(ALLOWED):
            failures.append(f"file outside the allow list tracked: {t}")
elif git.returncode == 0:
    failures.append(f"inside another Git repository ({top.stdout.strip()}), not this folder's own: tracked files not checkable")
else:
    print("\nNot a Git repository: tracked files NOT checked.")

if failures:
    print("\nNOT READY TO PUBLISH:")
    for f in failures:
        print("  " + f)
    sys.exit(1)
if in_repo:
    print("\nOK: docs/ matches release-files.txt, no draft content, all local links resolve, only allowed files tracked.")
else:
    print("\nOK for docs/ only: it matches release-files.txt, has no draft content and all local links resolve."
          "\nNOT CHECKED: tracked files. There is no Git repository yet; run this again in the repository before pushing.")
    sys.exit(2)  # incomplete: not a failure, but not a full pass either
