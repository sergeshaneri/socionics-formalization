#!/usr/bin/env python3
"""Render the Markdown with Pandoc and XeLaTeX."""
from pathlib import Path
import shutil
import subprocess

root=Path(__file__).resolve().parent
for executable in ['pandoc','xelatex']:
    if shutil.which(executable) is None:
        raise SystemExit(f'Missing PDF dependency: {executable}')
source=root/'2026-09-07-tencer-minaev-invariants.md'
target=root/'2026-09-07-tencer-minaev-invariants.pdf'
subprocess.run([
    'pandoc',str(source),'-o',str(target),'--pdf-engine=xelatex',
    '--from=markdown+tex_math_dollars+raw_tex','--standalone',
    '-V','documentclass=article','-V','papersize=a4','-V','fontsize=10pt',
    '-V','geometry=left=18mm,right=18mm,top=23mm,bottom=20mm',
    '-V','mainfont=DejaVu Serif','-V','sansfont=DejaVu Sans',
    '-V','monofont=DejaVu Sans Mono',
    '-V','colorlinks=true','-V','linkcolor=black','-V','urlcolor=blue',
    '-M','lang=ru-RU',
    '--include-in-header='+str(root/'pdf-header.tex'),
    '--lua-filter='+str(root/'pdf-layout.lua'),
],check=True)
print(target)
