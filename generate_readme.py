"""
generate_readme.py
──────────────────
Auto-generates README.md by scanning the repository for:
  - Jupyter notebooks (.ipynb)
  - Python scripts (.py)
  - Any new folders / modules

Fixes:
  - Description never returns raw code lines
  - Concepts extracted from ALL notebooks (fixed closure bug)

Run manually:  python generate_readme.py
Run via CI:    triggered by GitHub Actions on every push to main
"""

import os
import re
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# ── CONFIG ────────────────────────────────────────────────────────────────────
REPO_OWNER = "vineetm1204-m"
REPO_NAME  = "Deep-Learning-And-Neural-Network"
REPO_URL   = f"https://github.com/{REPO_OWNER}/{REPO_NAME}"
BRANCH     = "main"
AUTHOR     = "Vineet Mittal"
UNIVERSITY = "Amity University, Gwalior"

NOTEBOOK_EXTS = {".ipynb"}
SCRIPT_EXTS   = {".py"}
IGNORE_DIRS   = {".git", ".github", "__pycache__", "node_modules", ".ipynb_checkpoints"}
IGNORE_FILES  = {"generate_readme.py", "README.md"}


# ── GIT HELPERS ───────────────────────────────────────────────────────────────

def git_log(filepath, fmt="%ar"):
    try:
        r = subprocess.run(
            ["git", "log", "-1", f"--format={fmt}", "--", filepath],
            capture_output=True, text=True
        )
        return r.stdout.strip() or "—"
    except Exception:
        return "—"


def git_commit_count(filepath):
    try:
        r = subprocess.run(
            ["git", "log", "--oneline", "--", filepath],
            capture_output=True, text=True
        )
        return str(len([l for l in r.stdout.strip().splitlines() if l]))
    except Exception:
        return "1"


# ── NOTEBOOK PARSERS ──────────────────────────────────────────────────────────

def _load_nb(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def notebook_title(path):
    nb = _load_nb(path)
    if nb:
        for cell in nb.get("cells", []):
            if cell.get("cell_type") == "markdown":
                for line in "".join(cell.get("source", [])).splitlines():
                    line = line.strip()
                    if line.startswith("# "):
                        return line[2:].strip()
    return Path(path).stem.replace("-", " ").replace("_", " ").title()


def notebook_description(path):
    """
    Return a clean plain-text description.
    - Never returns raw code (code cells are skipped entirely).
    - Skips headings, fenced code, indented blocks.
    - Falls back to filename-derived sentence.
    """
    nb = _load_nb(path)
    if nb:
        for cell in nb.get("cells", []):
            if cell.get("cell_type") != "markdown":
                continue                          # skip code cells hard
            src = "".join(cell.get("source", []))
            for raw in src.splitlines():
                line = raw.strip()
                if not line:
                    continue
                if line.startswith(("#", "```", "    ", "\t")):
                    continue
                # Strip common markdown syntax
                clean = re.sub(r"[*_`\[\]()\->#|!]", "", line).strip()
                if len(clean) > 10:
                    return clean[:160] + ("…" if len(clean) > 160 else "")
    name = Path(path).stem.replace("-", " ").replace("_", " ").title()
    return f"Notebook covering {name}."


def notebook_tags(path):
    text = Path(path).stem.lower()
    keyword_map = {
        "forward":     ["forward-propagation"],
        "backprop":    ["backpropagation"],
        "cnn":         ["CNN", "convolution"],
        "alzheimer":   ["medical-imaging", "CNN"],
        "rnn":         ["RNN", "sequence"],
        "lstm":        ["LSTM"],
        "transformer": ["transformer", "attention"],
        "activation":  ["activation-functions"],
        "loss":        ["loss-functions"],
        "optim":       ["optimization"],
        "gradient":    ["gradient-descent"],
        "deep":        ["deep-learning"],
        "neural":      ["neural-network"],
        "multi":       ["multi-output"],
        "output":      ["multi-output"],
        "train":       ["training"],
        "data":        ["data-preprocessing"],
        "numpy":       ["numpy"],
        "keras":       ["keras"],
        "torch":       ["pytorch"],
        "tensorflow":  ["tensorflow"],
    }
    tags = []
    for kw, labels in keyword_map.items():
        if kw in text:
            tags.extend(labels)
    nb = _load_nb(path)
    if nb:
        full = " ".join(
            "".join(c.get("source", []))
            for c in nb.get("cells", [])
        ).lower()
        for kw, labels in keyword_map.items():
            if kw in full and labels[0] not in tags:
                tags.extend(labels)
    return list(dict.fromkeys(tags))[:6]


def extract_concepts(path):
    """
    Extract concepts from a notebook.

    Each ## / ### heading becomes one concept entry.
    Body = markdown text + code snippets until next heading.

    KEY FIX: flush() now takes `entry` as an explicit argument instead
    of relying on a closure over `current`. The old closure captured the
    variable binding, not the value — so when `current` was reassigned to
    a new dict for the next concept, flush() in the next notebook iteration
    would see the NEW (wrong) value rather than the one at flush-time.
    Passing explicitly makes every flush deterministic.
    """
    nb = _load_nb(path)
    if not nb:
        return []

    lang = nb.get("metadata", {}).get("kernelspec", {}).get("language", "python") or "python"
    cells = nb.get("cells", [])
    concepts = []
    current = None

    def flush(entry):
        """Commit entry to concepts list — entry passed explicitly, no closure."""
        if entry and entry.get("title"):
            body_str = "\n".join(entry["body"]).rstrip()
            concepts.append({"title": entry["title"], "body": body_str})

    for cell in cells:
        ctype  = cell.get("cell_type", "")
        source = "".join(cell.get("source", []))

        if ctype == "markdown":
            for line in source.splitlines():
                stripped = line.rstrip()
                if stripped.startswith("## ") or stripped.startswith("### "):
                    flush(current)                    # ← explicit arg, not closure
                    current = {"title": stripped.lstrip("#").strip(), "body": []}
                elif current is not None:
                    s = stripped.strip()
                    if s and not s.startswith("#"):
                        current["body"].append(stripped)

        elif ctype == "code":
            if current is not None and source.strip():
                code_lines = [l for l in source.splitlines() if l.strip()][:12]
                current["body"].append(f"```{lang}")
                current["body"].extend(code_lines)
                current["body"].append("```")

    flush(current)   # flush last entry

    # Fallback: no headings → bold lines as micro-concepts
    if not concepts:
        for cell in cells:
            if cell.get("cell_type") != "markdown":
                continue
            for line in "".join(cell.get("source", [])).splitlines():
                m = re.match(r"^\*\*(.+?)\*\*", line.strip())
                if m:
                    concepts.append({"title": m.group(1), "body": line.strip()})
            if len(concepts) >= 10:
                break

    return concepts


# ── REPO SCANNER ──────────────────────────────────────────────────────────────

def scan_repo(root):
    root = Path(root)
    notebooks, scripts, folders = [], [], []

    for item in sorted(root.rglob("*")):
        if any(p in IGNORE_DIRS for p in item.parts):
            continue
        if item.name in IGNORE_FILES:
            continue

        rel     = item.relative_to(root)
        rel_str = str(rel).replace(" ", "%20")

        if item.is_dir() and item != root:
            if not item.name.startswith("."):
                folders.append(str(rel))

        elif item.suffix in NOTEBOOK_EXTS:
            notebooks.append({
                "path":     str(rel),
                "name":     item.stem,
                "title":    notebook_title(item),
                "desc":     notebook_description(item),
                "tags":     notebook_tags(item),
                "updated":  git_log(str(rel)),
                "commits":  git_commit_count(str(rel)),
                "url":      f"{REPO_URL}/blob/{BRANCH}/{rel_str}",
                "colab":    f"https://colab.research.google.com/github/{REPO_OWNER}/{REPO_NAME}/blob/{BRANCH}/{rel_str}",
                "concepts": extract_concepts(item),
            })

        elif item.suffix in SCRIPT_EXTS:
            scripts.append({
                "path":    str(rel),
                "name":    item.stem,
                "updated": git_log(str(rel)),
                "url":     f"{REPO_URL}/blob/{BRANCH}/{rel_str}",
            })

    return {"notebooks": notebooks, "scripts": scripts, "folders": folders}


# ── README BUILDER ────────────────────────────────────────────────────────────

def build_readme(data):
    notebooks     = data["notebooks"]
    scripts       = data["scripts"]
    now           = datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC")
    nb_count      = len(notebooks)
    tag_count     = len({t for nb in notebooks for t in nb["tags"]})
    concept_count = sum(len(nb.get("concepts", [])) for nb in notebooks)

    lines = []

    # ── HEADER
    lines += [
        '<div align="center">',
        "",
        "# 🧠 Deep Learning & Neural Networks",
        "",
        "![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)",
        "![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white)",
        "![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)",
        "![Colab](https://img.shields.io/badge/Google_Colab-F9AB00?style=for-the-badge&logo=googlecolab&logoColor=white)",
        f"![Notebooks](https://img.shields.io/badge/Notebooks-{nb_count}-00e5ff?style=for-the-badge)",
        f"![Auto Updated](https://img.shields.io/badge/Auto_Updated-{now.replace(' ','_').replace(':','%3A')}-blueviolet?style=for-the-badge)",
        "",
        "**A hands-on exploration of forward propagation, neural network architecture,**",
        "**and the mathematics that power modern AI — built from scratch.**",
        "",
        "[📓 Notebooks](#-notebooks) · [🔬 Concepts](#-concepts-covered) · [🚀 Get Started](#-getting-started) · [📂 Structure](#-repository-structure)",
        "",
        "> 🤖 _This README is **auto-generated** on every push via GitHub Actions._",
        f"> Last updated: **{now}**",
        "",
        "</div>",
        "",
        "---",
        "",
    ]

    # ── STATS
    lines += [
        "## 📊 At a Glance",
        "",
        "| 📓 Notebooks | 🔬 Concepts | 🏷️ Topics | ⚡ Runtime |",
        "|:---:|:---:|:---:|:---:|",
        f"| **{nb_count}** | **{concept_count}** | **{tag_count}** | Jupyter / Colab |",
        "",
        "---",
        "",
    ]

    # ── NOTEBOOKS TABLE
    lines += ["## 📓 Notebooks", ""]

    if notebooks:
        lines += [
            "| # | Notebook | Description | Colab | Tags | Last Updated |",
            "|:---:|----------|-------------|:-----:|------|:---:|",
        ]
        for i, nb in enumerate(notebooks, 1):
            desc = nb["desc"].replace("|", "\\|").replace("`", "").replace("\n", " ").strip()
            desc = desc[:85] + ("…" if len(desc) > 85 else "")
            tags_str  = " ".join(f"`{t}`" for t in nb["tags"]) if nb["tags"] else "—"
            colab_btn = f"[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)]({nb['colab']})"
            lines.append(
                f"| {i} | [**{nb['title']}**]({nb['url']}) | {desc} | {colab_btn} | {tags_str} | {nb['updated']} |"
            )
        lines.append("")
    else:
        lines += ["> No notebooks found yet. Add `.ipynb` files and push!", ""]

    lines += ["---", ""]

    # ── CONCEPTS COVERED
    lines += ["## 🔬 Concepts Covered", ""]

    global_idx   = 1
    any_concepts = False

    for nb in notebooks:
        concepts = nb.get("concepts", [])
        if not concepts:
            continue
        any_concepts = True

        if len(notebooks) > 1:
            lines += [f"### 📓 [{nb['title']}]({nb['url']})", ""]

        for concept in concepts:
            title = concept["title"]
            body  = concept["body"]
            lines += [
                "<details>",
                f"<summary><strong>{global_idx:02d} · {title}</strong></summary>",
                "<br>",
                "",
                body if isinstance(body, str) else "\n".join(body),
                "",
                "</details>",
                "",
            ]
            global_idx += 1

    if not any_concepts:
        lines += [
            "> 📭 No `##` headings found in any notebook yet.",
            "> Add markdown headings inside your `.ipynb` cells —",
            "> they will appear here automatically on the next push.",
            "",
        ]

    lines += ["---", ""]

    # ── TECH STACK
    lines += [
        "## ⚙️ Tech Stack",
        "",
        "![Python](https://img.shields.io/badge/Python_3-3776AB?style=flat-square&logo=python&logoColor=white)",
        "![Jupyter](https://img.shields.io/badge/Jupyter_Notebook-F37626?style=flat-square&logo=jupyter&logoColor=white)",
        "![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white)",
        "![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=flat-square)",
        "![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=flat-square&logo=tensorflow&logoColor=white)",
        "![Keras](https://img.shields.io/badge/Keras-D00000?style=flat-square&logo=keras&logoColor=white)",
        "![Colab](https://img.shields.io/badge/Google_Colab_Ready-F9AB00?style=flat-square&logo=googlecolab&logoColor=white)",
        "",
        "---",
        "",
    ]

    # ── GETTING STARTED
    lines += [
        "## 🚀 Getting Started",
        "",
        "**1. Clone the repository**",
        "```bash",
        f"git clone {REPO_URL}.git",
        f"cd {REPO_NAME}",
        "```",
        "",
        "**2. Install dependencies**",
        "```bash",
        "pip install numpy matplotlib jupyter tensorflow keras",
        "```",
        "",
        "**3. Launch Jupyter**",
        "```bash",
        "jupyter notebook",
        "```",
        "",
        "**4. Or open directly in Colab** — click any badge in the [Notebooks](#-notebooks) table above.",
        "",
        "---",
        "",
    ]

    # ── REPO STRUCTURE
    lines += [
        "## 📂 Repository Structure",
        "",
        "```",
        f"{REPO_NAME}/",
        "│",
    ]
    for nb in notebooks:
        lines.append(f"├── 📓 {nb['path']}")
    for s in scripts:
        if s["name"] != "generate_readme":
            lines.append(f"├── 🐍 {s['path']}")
    lines += [
        "├── 📄 README.md              ← auto-generated",
        "└── 📁 .github/workflows/update-readme.yml",
        "```",
        "",
        "---",
        "",
    ]

    # ── AUTHOR
    lines += [
        "## 👤 Author",
        "",
        "<table><tr><td align='center'>",
        f"<b>{AUTHOR}</b><br>",
        f"<sub>BTech CSE · {UNIVERSITY}</sub><br><br>",
        f'<a href="https://github.com/{REPO_OWNER}">',
        f'<img src="https://img.shields.io/badge/GitHub-{REPO_OWNER}-181717?style=flat-square&logo=github" />',
        "</a>",
        "</td></tr></table>",
        "",
        "Building at the intersection of machine learning, web development, and web3.",
        "Currently working on my Technical Skills.",
        "Member of the **Amity Coding Club**.",
        "",
        "---",
        "",
    ]

    # ── CONTRIBUTING
    lines += [
        "## 🤝 Contributing",
        "",
        "1. Fork the repository",
        "2. Create your branch: `git checkout -b feature/your-notebook`",
        "3. Add your `.ipynb` file with `##` section headings",
        "4. Commit: `git commit -m 'Add: <topic> notebook'`",
        "5. Push & open a Pull Request",
        "",
        "> The README will **auto-update** to include your notebook and its concepts on the next push! 🎉",
        "",
        "---",
        "",
    ]

    # ── FOOTER
    lines += [
        "## ⭐ Support",
        "",
        "If this helped you understand deep learning fundamentals, drop a star!",
        "",
        f"[![Star on GitHub](https://img.shields.io/github/stars/{REPO_OWNER}/{REPO_NAME}?style=social)]({REPO_URL})",
        "",
        "---",
        "",
        '<div align="center">',
        f"  <sub>🤖 Auto-generated by <code>generate_readme.py</code> · {now} · "
        f"<a href='https://github.com/{REPO_OWNER}'>{AUTHOR}</a> · {UNIVERSITY}</sub>",
        "</div>",
    ]

    return "\n".join(lines) + "\n"


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    root = Path(__file__).parent.resolve()
    print(f"📁 Scanning: {root}")
    data = scan_repo(root)

    print(f"\n  📓 Notebooks : {len(data['notebooks'])}")
    for nb in data["notebooks"]:
        print(f"     • {nb['path']}")
        print(f"       desc     : {nb['desc'][:80]}")
        print(f"       tags     : {nb['tags']}")
        print(f"       concepts : {len(nb['concepts'])} found")
        for c in nb["concepts"]:
            print(f"         – {c['title']}")

    readme = build_readme(data)
    out = root / "README.md"
    out.write_text(readme, encoding="utf-8")
    print(f"\n✅ README.md written → {out}")


if __name__ == "__main__":
    main()
