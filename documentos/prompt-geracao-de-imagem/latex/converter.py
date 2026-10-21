"""Converte os quatro Markdown desta pasta em seções LaTeX legíveis.

Execute com: python3 converter.py
Requer markdown_it (python3-markdown-it), disponível no ambiente de autoria.
"""
from __future__ import annotations

import os
from pathlib import Path
from markdown_it import MarkdownIt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCES = [
    (ROOT / 'prompt-de-geracao-de-imagem.md', HERE / 'visao-geral.tex', 'visao-geral'),
    (ROOT / 'dicionario/prompt-de-geracao-de-imagem.md', HERE / 'dicionario.tex', 'dicionario'),
    (ROOT / 'hands-on/prompt-de-geracao-de-imagem.md', HERE / 'hands-on.tex', 'hands-on'),
    (ROOT / 'noticias/prompt-de-geracao-de-imagem.md', HERE / 'noticias.tex', 'noticias'),
]
LABELS = {src.resolve(): label for src, _, label in SOURCES}
MD = MarkdownIt('commonmark').enable('table')


def esc(s: str) -> str:
    replace = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$',
               '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}',
               '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'}
    return ''.join(replace.get(c, c) for c in s)


def inline(children, source: Path) -> str:
    out = []
    for t in children or []:
        kind = t.type
        if kind == 'text':
            out.append(esc(t.content))
        elif kind == 'code_inline':
            if ' ' not in t.content and (len(t.content) > 30 or any(c in t.content for c in '/_-')):
                out.append(r'\nolinkurl{' + t.content + '}')
            else:
                out.append(r'\texttt{' + esc(t.content) + '}')
        elif kind == 'strong_open':
            out.append(r'\textbf{')
        elif kind == 'strong_close':
            out.append('}')
        elif kind == 'em_open':
            out.append(r'\emph{')
        elif kind == 'em_close':
            out.append('}')
        elif kind == 'link_open':
            target = t.attrGet('href') or ''
            if not target.startswith(('http:', 'https:', '#')):
                resolved = (source.parent / target).resolve()
                if resolved in LABELS:
                    out.append(r'\hyperref[sec:' + LABELS[resolved] + ']{')
                    continue
                target = 'run:' + os.path.relpath(resolved, HERE)
            out.append(r'\href{' + target.replace('%', r'\%') + '}{')
        elif kind == 'link_close':
            out.append('}')
        elif kind == 'softbreak':
            out.append(' ')
        elif kind == 'hardbreak':
            out.append(r'\\')
        elif kind == 'html_inline':
            out.append(esc(t.content))
    return ''.join(out)


def render_table(tokens, source: Path) -> str:
    rows, row, cell = [], [], None
    for t in tokens:
        if t.type == 'tr_open':
            row = []
        elif t.type in ('th_open', 'td_open'):
            cell = ''
        elif t.type == 'inline' and cell is not None:
            cell += inline(t.children, source)
        elif t.type in ('th_close', 'td_close'):
            row.append(cell or '')
            cell = None
        elif t.type == 'tr_close':
            rows.append(row)
    if len(rows) < 2:
        return ''
    heads, body = rows[0], rows[1:]
    lines = []
    if not heads[0]:
        for col in range(1, len(heads)):
            lines += [r'\begin{recordbox}', r'{\bfseries\color{accent} ' + heads[col] + r'}\par']
            for row in body:
                if col < len(row):
                    lines.append(r'{\small\color{muted} ' + row[0] + r'}\quad ' + row[col] + r'\par')
            lines.append(r'\end{recordbox}')
    else:
        for row in body:
            if not row:
                continue
            lines += [r'\begin{recordbox}', r'{\bfseries\color{accent} ' + row[0] + r'}\par']
            for i in range(1, min(len(row), len(heads))):
                if row[i]:
                    lines.append(r'{\small\color{muted} ' + heads[i] + r'}\quad ' + row[i] + r'\par')
            lines.append(r'\end{recordbox}')
    return '\n'.join(lines) + '\n'


def convert(source: Path, dest: Path, label: str) -> None:
    tokens = MD.parse(source.read_text(encoding='utf-8'))
    lines = ['% Convertido de ' + os.path.relpath(source, HERE), '']
    i = 0
    while i < len(tokens):
        t = tokens[i]
        kind = t.type
        if kind == 'heading_open':
            heading = inline(tokens[i + 1].children, source)
            level = int(t.tag[1])
            if level == 1:
                lines += [r'\section{' + heading + r'}\label{sec:' + label + '}', '']
            else:
                lines += [r'\subsection*{' + heading + '}', '']
            i += 3
            continue
        if kind == 'paragraph_open':
            lines += [inline(tokens[i + 1].children, source), '']
            i += 3
            continue
        if kind == 'table_open':
            j = i + 1
            while tokens[j].type != 'table_close':
                j += 1
            lines += [render_table(tokens[i:j + 1], source), '']
            i = j + 1
            continue
        if kind in ('fence', 'code_block'):
            lines += [r'\begin{lstlisting}', t.content.rstrip('\n'), r'\end{lstlisting}', '']
        elif kind == 'blockquote_open':
            lines.append(r'\begin{sourcequote}')
        elif kind == 'blockquote_close':
            lines += [r'\end{sourcequote}', '']
        elif kind == 'bullet_list_open':
            lines.append(r'\begin{itemize}')
        elif kind == 'bullet_list_close':
            lines += [r'\end{itemize}', '']
        elif kind == 'ordered_list_open':
            lines.append(r'\begin{enumerate}')
        elif kind == 'ordered_list_close':
            lines += [r'\end{enumerate}', '']
        elif kind == 'list_item_open':
            lines.append(r'\item ')
        elif kind == 'list_item_close':
            lines.append('')
        elif kind == 'hr':
            lines.append(r'\noindent\color{rulecolor}\rule{\linewidth}{0.5pt}\color{ink}')
        i += 1
    dest.write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')


if __name__ == '__main__':
    for source, dest, label in SOURCES:
        convert(source, dest, label)
        print(dest.name)
