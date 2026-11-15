#!/usr/bin/env python3
"""Render a verified PDF page range for actual reading. Standard library only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


def find_tool(name, poppler_dir):
    executable = name + ('.exe' if os.name == 'nt' else '')
    candidates = []
    if poppler_dir:
        candidates.append(Path(poppler_dir) / executable)
    located = shutil.which(name)
    if located:
        candidates.append(Path(located))
    runtime = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies'
    candidates += [runtime / 'native/poppler/Library/bin' / executable,
                   runtime / 'bin/override' / executable,
                   runtime / 'bin/fallback' / executable]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    raise RuntimeError(f'{name} not found. Pass --poppler-dir with the Poppler bin directory.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('pdf', type=Path)
    p.add_argument('--start', required=True, type=int, help='First page, 1-based.')
    p.add_argument('--end', required=True, type=int, help='Last page, inclusive.')
    p.add_argument('--printed', action='store_true', help='Input uses printed body page numbers.')
    p.add_argument('--offset', type=int, default=19, help='PDF page minus printed page; verify after replacing book.')
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('--scale', type=int, default=2000)
    p.add_argument('--poppler-dir')
    a = p.parse_args()
    pdf = a.pdf.resolve(strict=True)
    if a.start < 1 or a.end < a.start or a.scale < 400:
        p.error('Require 1 <= start <= end and scale >= 400.')
    if a.end - a.start >= 30:
        p.error('Render at most 30 pages per batch; read them before rendering the next batch.')
    pdfinfo = find_tool('pdfinfo', a.poppler_dir)
    pdftoppm = find_tool('pdftoppm', a.poppler_dir)
    result = subprocess.run([pdfinfo, str(pdf)], capture_output=True, check=True, timeout=30)
    info = result.stdout.decode('utf-8', errors='replace')
    match = re.search(r'^Pages:\s+(\d+)', info, re.M)
    if not match:
        raise RuntimeError('Could not determine PDF page count.')
    count = int(match.group(1))
    first = a.start + (a.offset if a.printed else 0)
    last = a.end + (a.offset if a.printed else 0)
    if first < 1 or last > count:
        p.error(f'PDF range {first}–{last} is outside 1–{count}.')
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    prefix = out / f'pdf-{first:03d}-{last:03d}'
    subprocess.run([pdftoppm, '-f', str(first), '-l', str(last), '-scale-to', str(a.scale),
                    '-png', str(pdf), str(prefix)], check=True, capture_output=True, timeout=180)
    files = sorted(out.glob(prefix.name + '-*.png'))
    pages = []
    for image in files:
        page = int(image.stem.rsplit('-', 1)[1])
        if first <= page <= last:
            pages.append({'pdfPage': page, 'printedPage': page - a.offset if a.printed else None,
                          'image': str(image)})
    if len(pages) != last - first + 1:
        raise RuntimeError('Rendering did not produce every requested page.')
    digest = hashlib.sha256()
    with pdf.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    manifest = {'source': str(pdf), 'sourceSha256': digest.hexdigest(), 'pdfPages': count,
                'printedOffset': a.offset if a.printed else None, 'pages': pages,
                'status': 'rendered-not-yet-read'}
    manifest_path = prefix.with_suffix('.pages.json')
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'manifest': str(manifest_path), 'pages': pages}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f'Page rendering failed: {exc}', file=sys.stderr)
        sys.exit(1)
