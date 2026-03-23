"""
generate_readme.py
──────────────────
Auto-generates README.md by scanning the repository for:
  - Jupyter notebooks (.ipynb)
  - Python scripts (.py)
  - Any new folders / modules

Run manually:  python generate_readme.py
Run via CI:    triggered by GitHub Actions on every push to main
"""

import os
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

# File types to scan
NOTEBOOK_EXTS = {".ipynb"}
SCRIPT_EXTS   = {".py"}
IGNORE_DIRS   = {".git", ".github", "__pycache__", "node_modules", ".ipynb_checkpoints"}
IGNORE_FILES  = {"generate_readme.py", "README.md"}

# ── HELPERS ───────────────────────────────────────────────────────────────────

def git_log(filepath: str, fmt: str = "%ar") -> str:
    """Return last-commit info for a file."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", f"--format={fmt}", "--", filepath],
            capture_output=True, text=True
        )
        return result.stdout.strip() or "—"
    except Exception:
        return "—"


def git_commit_count(filepath: str) -> str:
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "--", filepath],
            capture_output=True, text=True
        )
        lines = [l for l in result.stdout.strip().splitlines() if l]
        return str(len(lines))
    except Exception:
        return "1"


def notebook_title(path: Path) -> str:
    """Extract first H1 from notebook markdown cells, else use filename."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            nb = json.load(f)
        for cell in nb.get("cells", []):
            if cell.get("cell_type") == "markdown":
                for line in cell.get("source", []):
                    line = line.strip()
                    if line.startswith("# "):
                        return line[2:].strip()
    except Exception:
        pass
    return path.stem.replace("-", " ").replace("_", " ").title()


def notebook_description(path: Path) -> str:
    """Extract first non-heading markdown text from notebook."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            nb = json.load(f)
        found_heading = False
        for cell in nb.get("cells", []):
            if cell.get("cell_type") == "markdown":
                src = "".join(cell.get("source", []))
                lines = src.strip().splitlines()
                for line in lines:
                    line = line.strip()
                    if line.startswith("#"):
                        found_heading = True
                        continue
                    if found_heading and line and not line.startswith("#"):
                        return line[:180] + ("…" if len(line) > 180 else "")
            elif cell.get("cell_type") == "code" and found_heading:
                src = "".join(cell.get("source", [])).strip()
                if src:
                    return f"`{src[:100]}{'…' if len(src)>100 else ''}`"
    except Exception:
        pass
    return "Deep learning notebook — open to explore."


def extract_concepts(path: Path) -> list[dict]:
    """
    Extract concepts dynamically from a notebook by reading every cell.

    Strategy:
      - Every markdown H2 (##) or H3 (###) heading becomes a concept entry.
      - The body of that concept is built from the cells that follow until
        the next heading: markdown text is kept as-is, code cells are
        wrapped in a fenced code block (language auto-detected from
        the notebook kernel or first-line shebang / import).
      - H1 (#) is treated as the notebook title, not a concept.
      - If no headings exist at all, falls back to collecting all
        top-level markdown bold lines (**text**) as lightweight concepts.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            nb = json.load(f)
    except Exception:
        return []

    # Detect kernel language for code fences
    lang = (
        nb.get("metadata", {})
          .get("kernelspec", {})
          .get("language", "python")
    ) or "python"

    cells = nb.get("cells", [])
    concepts: list[dict] = []
    current: dict | None = None

    def flush():
        if current and current.get("title"):
            # Clean up trailing blank lines in body
            body = "\n".join(current["body"]).rstrip()
            concepts.append({"title": current["title"], "body": body})

    for cell in cells:
        ctype  = cell.get("cell_type", "")
        source = "".join(cell.get("source", []))

        if ctype == "markdown":
            lines = source.splitlines()
            i = 0
            while i < len(lines):
                line = lines[i].rstrip()

                # H2 / H3 → new concept
                if line.startswith("## ") or line.startswith("### "):
                    flush()
                    title = line.lstrip("#").strip()
                    current = {"title": title, "body": []}
                    # Collect remaining lines of THIS cell after the heading
                    rest = lines[i + 1:]
                    if rest:
                        # Find next heading within same cell
                        for j, rl in enumerate(rest):
                            if rl.startswith("## ") or rl.startswith("### "):
                                flush()
                                title2 = rl.lstrip("#").strip()
                                current = {"title": title2, "body": []}
                                rest = rest[j + 1:]
                                break
                            else:
                                if current:
                                    current["body"].append(rl)
                    break  # handled whole cell
                else:
                    # Lines before first heading in this cell → append to current concept
                    if current and line:
                        current["body"].append(line)
                i += 1

        elif ctype == "code":
            if current is not None and source.strip():
                # Limit code snippets to first 15 non-empty lines
                code_lines = [l for l in source.splitlines() if l.strip()][:15]
                snippet = "\n".join(code_lines)
                current["body"].append(f"```{lang}")
                current["body"].append(snippet)
                current["body"].append("```")

    flush()

    # ── Fallback: no headings found → use bold lines as micro-concepts
    if not concepts:
        import re
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


def notebook_tags(path: Path) -> list[str]:
    """Guess tags from notebook filename and cell content."""
    text = path.stem.lower()
    tags = []
    keyword_map = {
        "forward": ["forward-propagation"],
        "backprop": ["backpropagation"],
        "cnn": ["CNN", "convolution"],
        "rnn": ["RNN", "sequence"],
        "lstm": ["LSTM"],
        "transformer": ["transformer", "attention"],
        "activation": ["activation-functions"],
        "loss": ["loss-functions"],
        "optim": ["optimization"],
        "gradient": ["gradient-descent"],
        "deep": ["deep-learning"],
        "neural": ["neural-network"],
        "train": ["training"],
        "data": ["data-preprocessing"],
        "visual": ["visualization"],
        "numpy": ["numpy"],
        "keras": ["keras"],
        "torch": ["pytorch"],
        "tensorflow": ["tensorflow"],
    }
    for kw, labels in keyword_map.items():
        if kw in text:
            tags.extend(labels)

    try:
        with open(path, "r", encoding="utf-8") as f:
            nb = json.load(f)
        full_text = " ".join(
            "".join(c.get("source", []))
            for c in nb.get("cells", [])
        ).lower()
        for kw, labels in keyword_map.items():
            if kw in full_text and labels[0] not in tags:
                tags.extend(labels)
    except Exception:
        pass

    return list(dict.fromkeys(tags))[:6]  # dedupe, max 6


def scan_repo(root: Path) -> dict:
    """Walk repo and collect notebooks, scripts, folders."""
    notebooks = []
    scripts   = []
    folders   = []

    for item in sorted(root.rglob("*")):
        # Skip ignored
        if any(p in IGNORE_DIRS for p in item.parts):
            continue
        if item.name in IGNORE_FILES:
            continue

        rel = item.relative_to(root)

        if item.is_dir() and item != root:
            if item.name not in IGNORE_DIRS and not item.name.startswith("."):
                folders.append(str(rel))

        elif item.suffix in NOTEBOOK_EXTS:
            notebooks.append({
                "path":    str(rel),
                "name":    item.stem,
                "title":   notebook_title(item),
                "desc":    notebook_description(item),
                "tags":    notebook_tags(item),
                "updated": git_log(str(rel)),
                "commits": git_commit_count(str(rel)),
                "url":      f"{REPO_URL}/blob/{BRANCH}/{str(rel).replace(' ', '%20')}",
                "colab":    f"https://colab.research.google.com/github/{REPO_OWNER}/{REPO_NAME}/blob/{BRANCH}/{str(rel).replace(' ', '%20')}",
                "concepts": extract_concepts(item),
            })

        elif item.suffix in SCRIPT_EXTS:
            scripts.append({
                "path":    str(rel),
                "name":    item.stem,
                "updated": git_log(str(rel)),
                "url":     f"{REPO_URL}/blob/{BRANCH}/{str(rel).replace(' ', '%20')}",
            })

    return {"notebooks": notebooks, "scripts": scripts, "folders": folders}


# ── README BUILDER ────────────────────────────────────────────────────────────

def build_readme(data: dict) -> str:
    notebooks = data["notebooks"]
    scripts   = data["scripts"]
    now       = datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC")
    nb_count      = len(notebooks)
    tag_count     = len({t for nb in notebooks for t in nb["tags"]})
    concept_count = sum(len(nb.get("concepts", [])) for nb in notebooks)

    # ── HEADER
    lines = [
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
        f"| 📓 Notebooks | 🔬 Concepts | 🏷️ Topics | ⚡ Runtime |",
        f"|:---:|:---:|:---:|:---:|",
        f"| **{nb_count}** | **{concept_count}** | **{tag_count}** | Jupyter / Colab |",
        "",
        "---",
        "",
    ]

    # ── NOTEBOOKS TABLE
    lines += [
        "## 📓 Notebooks",
        "",
    ]

    if notebooks:
        lines += [
            "| # | Notebook | Description | Colab | Tags | Last Updated |",
            "|---|----------|-------------|:-----:|------|-------------|",
        ]
        for i, nb in enumerate(notebooks, 1):
            tags_str  = " ".join(f"`{t}`" for t in nb["tags"]) if nb["tags"] else "—"
            desc      = nb["desc"].replace("|", "\\|")[:80] + ("…" if len(nb["desc"]) > 80 else "")
            colab_btn = f"[![Open](https://colab.research.google.com/assets/colab-badge.svg)]({nb['colab']})"
            lines.append(
                f"| {i} | [**{nb['title']}**]({nb['url']}) | {desc} | {colab_btn} | {tags_str} | {nb['updated']} |"
            )
        lines.append("")
    else:
        lines += ["> No notebooks found yet. Add `.ipynb` files and push!", ""]

    lines += ["---", ""]

    # ── CONCEPTS COVERED (dynamically extracted from notebook cells) ────────────
    lines += ["## 🔬 Concepts Covered", ""]

    # Gather all concepts across every notebook, grouped by notebook
    all_concepts_found = False
    for nb in notebooks:
        concepts = nb.get("concepts", [])
        if not concepts:
            continue
        all_concepts_found = True

        # Show notebook source label only when there are multiple notebooks
        if len(notebooks) > 1:
            lines += [
                f"### 📓 From: [{nb['title']}]({nb['url']})",
                "",
            ]

        for idx, concept in enumerate(concepts, 1):
            title = concept["title"]
            body  = concept["body"]

            lines += [
                "<details>",
                f"<summary><strong>{idx:02d} · {title}</strong></summary>",
                "<br>",
                "",
            ]

            if isinstance(body, list):
                lines += body
            else:
                lines.append(str(body))

            lines += ["", "</details>", ""]

    if not all_concepts_found:
        lines += [
            "> 📭 No section headings found in notebooks yet.",
            "> Add `##` headings inside your `.ipynb` markdown cells and they will",
            "> automatically appear here as expandable concept entries on the next push.",
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
        "pip install numpy matplotlib jupyter",
        "```",
        "",
        "**3. Launch Jupyter**",
        "```bash",
        'jupyter notebook',
        "```",
        "",
        "**4. Or open directly in Colab** — click any badge in the [Notebooks](#-notebooks) section above.",
        "",
        "---",
        "",
    ]

    # ── REPO STRUCTURE (auto-generated)
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
        "├── 📄 README.md  ← auto-generated",
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
        "Building at the intersection of machine learning, web development, and agri-tech.",
        "Currently working on **KrishiMitra** (smart farming ML platform) and **ToyBill** (GST billing app).",
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
        "3. Add your `.ipynb` file",
        "4. Commit: `git commit -m 'Add: <topic> notebook'`",
        "5. Push & open a Pull Request",
        "",
        "> The README will **auto-update** to include your notebook on the next push! 🎉",
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
        f"  <sub>🤖 Auto-generated by <code>generate_readme.py</code> · {now} · <a href='https://github.com/{REPO_OWNER}'>{AUTHOR}</a> · {UNIVERSITY}</sub>",
        "</div>",
    ]

    return "\n".join(lines) + "\n"


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    root = Path(__file__).parent.resolve()
    print(f"📁 Scanning: {root}")

    data = scan_repo(root)

    print(f"  📓 Notebooks found : {len(data['notebooks'])}")
    for nb in data["notebooks"]:
        print(f"     • {nb['path']}  [{nb['updated']}]  tags: {nb['tags']}")
    print(f"  🐍 Scripts found   : {len(data['scripts'])}")

    readme = build_readme(data)

    out = root / "README.md"
    out.write_text(readme, encoding="utf-8")
    print(f"\n✅ README.md written → {out}")


if __name__ == "__main__":
    main()