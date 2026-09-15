#!/usr/bin/env python3
"""Minimal Markdown -> LaTeX for MP1_report.md (headings, lists, tables,
$$ math $$, inline $math$, **bold**, `code`, and the Figure 1 placeholder,
which is replaced by a TikZ plot of the Monte Carlo periods from sim.log)."""
import re, sys

md_path, simlog, out_path, repo_url = sys.argv[1:5]
lines = open(md_path).read().splitlines()

# ---------------------------------------------------------------- MC data
txt = open(simlog, errors="ignore").read()
m = re.search(r"Measurement: period\s*\n\s*step\s+t2-t1\s*\n(.*?)(?:\n\s*\n|\Z)", txt, re.S)
periods = [float(l.split()[1]) for l in m.group(1).strip().splitlines() if l.split()[0].isdigit()]

def figure():
    # 500 points scaled: x = run/500*12 cm, y = (T-0.85)/0.3*6 cm  (0.85..1.15 s)
    pts = " ".join(f"({i/len(periods)*12:.3f},{(t-0.85)/0.30*6:.3f})" for i, t in enumerate(periods, 1))
    yt = "".join(f"\\draw ({-0.1},{(v-0.85)/0.30*6:.3f}) -- ({0},{(v-0.85)/0.30*6:.3f}) node[left,xshift=-2pt]{{\\footnotesize {v:.2f}}};\n"
                 for v in (0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15))
    xt = "".join(f"\\draw ({r/500*12:.3f},-0.1) -- ({r/500*12:.3f},0) node[below,yshift=-2pt]{{\\footnotesize {r}}};\n"
                 for r in (0, 100, 200, 300, 400, 500))
    mean = sum(periods) / len(periods)
    return rf"""
\begin{{figure}}[htbp]
\centering
\begin{{tikzpicture}}
\draw[black] (0,0) rectangle (12,6);
{yt}{xt}
\draw[red,dashed,thick] (0,{(0.9-0.85)/0.3*6:.3f}) -- (12,{(0.9-0.85)/0.3*6:.3f}) node[right,xshift=2pt]{{\footnotesize 0.9 s}};
\draw[red,dashed,thick] (0,{(1.1-0.85)/0.3*6:.3f}) -- (12,{(1.1-0.85)/0.3*6:.3f}) node[right,xshift=2pt]{{\footnotesize 1.1 s}};
\draw[gray,dotted] (0,{(1.0-0.85)/0.3*6:.3f}) -- (12,{(1.0-0.85)/0.3*6:.3f});
\foreach \p in {{{pts}}} \fill[blue!70!black] \p circle (1.1pt);
\node[below=14pt] at (6,0) {{Monte Carlo run number}};
\node[rotate=90,left=26pt] at (0,3) {{Measured period (s)}};
\end{{tikzpicture}}
\caption{{Period of each of the 500 LTspice Monte Carlo runs (1\% resistors, 5\% capacitor). The dashed lines at 0.9 s and 1.1 s are the $\pm 10$\% limits; every run is inside them. Mean {mean:.3f} s, min {min(periods):.3f} s, max {max(periods):.3f} s.}}
\end{{figure}}
"""

# ------------------------------------------------------------ inline text
def esc(s):
    return (s.replace("\\", r"\textbackslash{}").replace("&", r"\&").replace("%", r"\%")
             .replace("#", r"\#").replace("_", r"\_").replace("~", r"\textasciitilde{}")
             .replace("^", r"\textasciicircum{}"))

def inline(s):
    if "**" in s:
        parts = s.split("**")
        return "".join((r"\textbf{" + inline(p) + "}") if k % 2 else inline(p) for k, p in enumerate(parts))
    s = s.replace("mm^2", "mm$^2$").replace("+/-", "$\\pm$")
    out, i = [], 0
    # split on inline math and code spans, escape the rest
    for tok in re.split(r"(\$[^$]+\$|`[^`]+`)", s):
        if not tok:
            continue
        if tok.startswith("$"):
            out.append(tok)
        elif tok.startswith("`"):
            out.append(r"\texttt{" + esc(tok[1:-1]) + "}")
        else:
            t = esc(tok)
            t = re.sub(r"\\\*\\\*(.+?)\\\*\\\*", r"\\textbf{\1}", t)   # (won't match; ** not escaped)
            t = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", t)
            t = t.replace("--", "--")
            out.append(t)
    return "".join(out)

# ------------------------------------------------------------- converter
out = []
i = 0
def flush_list(kind, items):
    env = "itemize" if kind == "-" else "enumerate"
    out.append(rf"\begin{{{env}}}")
    for it in items:
        out.append(r"\item " + inline(it))
    out.append(rf"\end{{{env}}}")

while i < len(lines):
    ln = lines[i]
    if ln.startswith("# "):
        out.append(r"\title{" + inline(ln[2:]) + r"}\author{Dhvan Shah}\date{September 2026}\maketitle"); i += 1; continue
    if ln.startswith("## "):
        out.append(r"\section*{" + inline(ln[3:]) + "}"); i += 1; continue
    if ln.startswith("### "):
        out.append(r"\subsection*{" + inline(ln[4:]) + "}"); i += 1; continue
    if ln.strip() == "$$":
        j = i + 1; body = []
        while lines[j].strip() != "$$":
            body.append(lines[j]); j += 1
        out.append(r"\[" + "\n" + "\n".join(body) + "\n" + r"\]"); i = j + 1; continue
    if ln.startswith("[FIGURE 1 HERE"):
        out.append(figure()); i += 1; continue
    mi = re.match(r"^!\[(.*)\]\((.+)\)\s*$", ln)
    if mi:
        cap, src = mi.group(1), mi.group(2)
        out.append(r"\begin{figure}[htbp]\centering\includegraphics[width=\textwidth]{" + src + "}"
                   + (r"\caption{" + inline(cap) + "}" if cap else "") + r"\end{figure}")
        i += 1; continue
    if ln.startswith("|"):
        rows = []
        while i < len(lines) and lines[i].startswith("|"):
            rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
        header, body = rows[0], rows[2:]
        n = len(header)
        if n >= 8:   # BOM: wide table, landscape page
            spec = r"r l c l p{3.8cm} l l c p{3.4cm}"
            out.append(r"\begin{landscape}\begin{scriptsize}\begin{tabular}{" + spec + "}")
        else:
            spec = " ".join("l" * n)
            out.append(r"\begin{center}\begin{tabular}{" + spec + "}")
        out.append(r"\toprule")
        out.append(" & ".join(inline(c) for c in header) + r" \\ \midrule")
        for r in body:
            out.append(" & ".join(inline(c) for c in r) + r" \\")
        out.append(r"\bottomrule")
        out.append(r"\end{tabular}\end{scriptsize}\end{landscape}" if n >= 8 else r"\end{tabular}\end{center}")
        out.append("")
        continue
    if re.match(r"^- ", ln) or re.match(r"^\d+\. ", ln):
        kind = "-" if ln.startswith("- ") else "1"
        items = []
        while i < len(lines) and (re.match(r"^- ", lines[i]) if kind == "-" else re.match(r"^\d+\. ", lines[i])):
            items.append(re.sub(r"^(- |\d+\. )", "", lines[i])); i += 1
        flush_list(kind, items); continue
    if ln.strip() == "":
        out.append(""); i += 1; continue
    if re.match(r"^https?://\S+$", ln.strip()):
        out.append(r"\begin{center}\url{" + ln.strip() + "}\end{center}"); i += 1; continue
    out.append(inline(ln)); i += 1



doc = r"""\documentclass[11pt,letterpaper]{article}
\usepackage{fontspec}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{booktabs,tabularx}
\usepackage{tikz}\usepackage{graphicx}\graphicspath{{""" + __import__('os').path.dirname(__import__('os').path.abspath(md_path)) + r"""/}}
\usepackage{microtype}\usepackage{pdflscape}
\usepackage[hidelinks]{hyperref}
\setlength{\parskip}{6pt}\setlength{\parindent}{0pt}
\begin{document}
""" + "\n".join(out) + "\n\\end{document}\n"
open(out_path, "w").write(doc)
print("wrote", out_path, "with", len(periods), "MC points")
