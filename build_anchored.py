#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bridging script: Generates anchored copies and index from canonical skill repository.
Canonical source files remain untouched; build products are read-only.

Usage:
  python build_anchored.py
  python build_anchored.py --repo <repo_path>
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

OPEN = Path(__file__).resolve().parent
PRO = OPEN.parent / 'vedic-astro-skills-pro'
SKILL_REL = Path('skills/vedic-core')

FILES = {
    'SKILL.md': 'SK',
    'resources/p1_p12.md': 'P12',
    'resources/yogas.md': 'YG',
    'resources/house_framework.md': 'HF',
    'resources/qa_rules.md': 'QA',
    'resources/prediction_rules.md': 'PR',
    'resources/synthesis.md': 'SY',
}

RE_HEADING = re.compile(r'^(#{2,3})\s+(.+)$')
RE_WARN = re.compile(r'^\s*[>\-\*\s]*⚠️')
RE_L3 = re.compile(r'^\s*\d+\.\s+\*\*')
RE_NUMLIST = re.compile(r'^\s*1\.\s+\S')


def anchor_id(abbr: str, first_line: str) -> str:
    h = hashlib.sha1(first_line.strip().encode('utf-8')).hexdigest()[:8]
    return f'A-{abbr}-{h}'


def clean_title(line: str, maxlen: int = 80) -> str:
    t = re.sub(r'^[#>\s\-\*]+', '', line).strip().strip('`*')
    return t[:maxlen]


def parse_file(text: str, abbr: str, relname: str):
    """Scan line by line, producing (anchored_lines, anchors[])."""
    lines = text.split('\n')
    out, anchors = [], []
    i, n = 0, len(lines)
    in_code = False

    def emit(level: str, first_line: str, block_lines: list):
        aid = anchor_id(abbr, first_line)
        anchors.append({
            'id': aid, 'file': relname, 'level': level,
            'title': clean_title(first_line),
            'text': '\n'.join(block_lines).strip(),
        })
        out.append(f'<!-- ANCHOR: {aid} {level} -->')

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith('```') and not in_code:
            j = i + 1
            while j < n and not lines[j].strip().startswith('```'):
                j += 1
            block = lines[i:min(j + 1, n)]
            first = next((l for l in block[1:] if l.strip()), block[0])
            emit('L2', first, block)
            out.extend(block)
            i = j + 1
            continue

        m = RE_HEADING.match(line)
        if m:
            emit('L1', m.group(2), [line])
            out.append(line)
            i += 1
            continue

        if RE_WARN.match(line):
            j = i
            while j < n and lines[j].strip():
                j += 1
            emit('L2', line, lines[i:j])
            out.extend(lines[i:j])
            i = j
            continue

        if RE_L3.match(line):
            j = i + 1
            while j < n and lines[j].strip() and not RE_L3.match(lines[j]) \
                    and not RE_HEADING.match(lines[j]) and not lines[j].strip().startswith('```'):
                j += 1
            emit('L3', line, lines[i:j])
            out.extend(lines[i:j])
            i = j
            continue

        if RE_NUMLIST.match(line) and not RE_L3.match(line):
            j = i
            while j < n and lines[j].strip() and not RE_HEADING.match(lines[j]) \
                    and not lines[j].strip().startswith('```'):
                j += 1
            emit('L2', line, lines[i:j])
            out.extend(lines[i:j])
            i = j
            continue

        if stripped.startswith('>'):
            j = i
            while j < n and lines[j].strip().startswith('>'):
                j += 1
            emit('L2', line, lines[i:j])
            out.extend(lines[i:j])
            i = j
            continue

        out.append(line)
        i += 1

    return '\n'.join(out), anchors


def compute_sections(text: str, abbr: str, relname: str):
    lines = text.split('\n')
    sections = []
    in_code = False
    cur = None

    def flush():
        if cur is not None:
            body = '\n'.join(cur['lines'])
            sections.append({
                'anchor': anchor_id(abbr, cur['heading']),
                'file': relname,
                'title': clean_title(cur['heading']),
                'section_hash': hashlib.sha1(body.encode('utf-8')).hexdigest()[:12],
                'n_lines': len(cur['lines']),
            })

    for line in lines:
        if line.strip().startswith('```'):
            in_code = not in_code
        m = RE_HEADING.match(line) if not in_code else None
        if m:
            flush()
            cur = {'heading': m.group(2), 'lines': [line]}
        elif cur is not None:
            cur['lines'].append(line)
    flush()
    return sections


def git_commit(repo: Path) -> str:
    rel = str(SKILL_REL).replace('\\', '/')
    pathspec = [f'{rel}/{f}' for f in FILES]
    try:
        r = subprocess.run(
            ['git', '-C', str(repo), 'log', '-1', '--format=%H', '--', *pathspec],
            capture_output=True, text=True)
        out = r.stdout.strip()[:12]
        if out:
            return out
        head = subprocess.run(['git', '-C', str(repo), 'rev-parse', 'HEAD'],
                              capture_output=True, text=True).stdout.strip()[:12]
        return f'{head}-HEAD-fallback' if head else 'unknown'
    except Exception:
        return 'unknown'


def build(repo: Path) -> dict:
    src_dir = repo / SKILL_REL
    out_dir = repo / 'build' / 'anchored'
    out_dir.mkdir(parents=True, exist_ok=True)
    all_anchors = []
    all_sections = []
    file_hashes = {}
    for rel, abbr in FILES.items():
        p = src_dir / rel
        if not p.exists():
            continue
        text = p.read_text(encoding='utf-8')
        anchored, anchors = parse_file(text, abbr, rel)
        (out_dir / (Path(rel).name + '.anchored.md')).write_text(anchored, encoding='utf-8')
        all_anchors.extend(anchors)
        all_sections.extend(compute_sections(text, abbr, rel))
        file_hashes[rel] = hashlib.sha1(text.encode('utf-8')).hexdigest()[:12]
    index = {
        'source_commit': git_commit(repo),
        'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'repo': repo.name,
        'anchor_count': len(all_anchors),
        'section_count': len(all_sections),
        'file_hashes': file_hashes,
        'anchors': all_anchors,
        'sections': all_sections,
    }
    (out_dir / 'rule_index.json').write_text(
        json.dumps(index, ensure_ascii=False, indent=1), encoding='utf-8')
    by = {}
    for a in all_anchors:
        by[a['level']] = by.get(a['level'], 0) + 1
    print(f'  {repo.name}: {len(all_anchors)} anchors '
          f'(L1={by.get("L1",0)} L2={by.get("L2",0)} L3={by.get("L3",0)}) '
          f'+ {len(all_sections)} sections(hash) -> {out_dir}')
    return index


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', help='Target repository root path')
    ap.add_argument('--pro', help='Pro repo path')
    args = ap.parse_args()
    if args.repo:
        targets = [Path(args.repo)]
    else:
        pro = Path(args.pro) if args.pro else PRO
        targets = [OPEN]
        if pro.exists():
            targets.append(pro)
    for r in targets:
        if not r.exists():
            sys.exit(f'[FATAL] repo not found: {r}')
        build(r)
    print('Done. Note: build/anchored/ artifacts are read-only; re-run this script to rebuild.')
