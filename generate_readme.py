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
IGNORE_DIRS   = {".git", ".github", ".venv", "__pycache__", "node_modules", ".ipynb_checkpoints"}
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
                "url":     f"{REPO_URL}/blob/{BRANCH}/{str(rel).replace(' ', '%20')}",
                "colab":   f"https://colab.research.google.com/github/{REPO_OWNER}/{REPO_NAME}/blob/{BRANCH}/{str(rel).replace(' ', '%20')}",
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
    nb_count  = len(notebooks)
    tag_count = len({t for nb in notebooks for t in nb["tags"]})

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
        f"| 📓 Notebooks | 🏷️ Topics | 🌐 Language | ⚡ Runtime |",
        f"|:---:|:---:|:---:|:---:|",
        f"| **{nb_count}** | **{tag_count}** | Python 3 | Jupyter / Colab |",
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
            "| # | Notebook | Description | Tags | Last Updated |",
            "|---|----------|-------------|------|-------------|",
        ]
        for i, nb in enumerate(notebooks, 1):
            tags_str = " ".join(f"`{t}`" for t in nb["tags"]) if nb["tags"] else "—"
            raw_desc = nb["desc"] or "Deep learning notebook — open to explore."
            safe_desc = " ".join(raw_desc.split())  # collapse newlines/extra spaces to keep table layout intact
            safe_desc = safe_desc.replace("|", "\\|")
            desc = safe_desc[:90] + ("…" if len(safe_desc) > 90 else "")
            lines.append(
                f"| {i} | [**{nb['title']}**]({nb['url']}) | {desc} | {tags_str} | {nb['updated']} |"
            )
        lines.append("")

        # Colab buttons
        lines += ["### ▶️ Open in Google Colab", ""]
        for nb in notebooks:
            lines.append(
                f"[![{nb['title']}](https://colab.research.google.com/assets/colab-badge.svg)]({nb['colab']}) `{nb['path']}`"
            )
        lines.append("")
    else:
        lines += ["> No notebooks found yet. Add `.ipynb` files and push!", ""]

    lines += ["---", ""]

    # ── CONCEPTS ACCORDION (static but comprehensive)
    lines += [
        "## 🔬 Concepts Covered",
        "",
        "<details>",
        "<summary><strong>01 · Neural Network Fundamentals</strong></summary><br>",
        "",
        "A neural network is a computational graph of interconnected nodes (neurons) arranged in layers.",
        "",
        "```",
        "Input Layer → Hidden Layer(s) → Output Layer",
        "```",
        "",
        "</details>",
        "",
        "<details>",
        "<summary><strong>02 · Forward Propagation</strong></summary><br>",
        "",
        "At each layer, forward propagation computes:",
        "",
        "```python",
        "Z = np.dot(W, X) + b   # Weighted sum",
        "A = activation(Z)       # Apply activation",
        "```",
        "",
        "</details>",
        "",
        "<details>",
        "<summary><strong>03 · Weight & Bias Initialization</strong></summary><br>",
        "",
        "```python",
        "W = np.random.randn(n_out, n_in) * 0.01  # Break symmetry",
        "b = np.zeros((n_out, 1))                  # Zero biases",
        "```",
        "",
        "</details>",
        "",
        "<details>",
        "<summary><strong>04 · Activation Functions</strong></summary><br>",
        "",
        "| Function | Formula | Use Case |",
        "|----------|---------|----------|",
        "| ReLU | `max(0, z)` | Hidden layers |",
        "| Sigmoid | `1 / (1 + e⁻ᶻ)` | Binary output |",
        "| Softmax | `eᶻⁱ / Σeᶻ` | Multi-class |",
        "",
        "</details>",
        "",
        "<details>",
        "<summary><strong>05 · Deep vs Shallow Networks</strong></summary><br>",
        "",
        "- **Shallow**: 1 hidden layer — simpler, less expressive",
        "- **Deep**: 2+ hidden layers — hierarchical features, needs careful training",
        "",
        "</details>",
        "",
        "<details>",
        "<summary><strong>06 · Vectorized NumPy Operations</strong></summary><br>",
        "",
        "```python",
        "Z   = np.dot(W, X) + b       # Entire batch at once",
        "A   = np.maximum(0, Z)        # ReLU — no loops",
        "sig = 1 / (1 + np.exp(-Z))   # Sigmoid",
        "```",
        "",
        "</details>",
        "",
        "---",
        "",
    ]

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
        "Building at the intersection of machine learning, web development, and web3.",
        "Currently working on my technical skills.",
        f"Member of the **Amity Coding Club**.",
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
