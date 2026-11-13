#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Repository to platform copies synchronizer ("Repo as canonical source").

Canonical source = <repo>/skills/

Subcommands:
  platforms  Sync in-repo skills/ → claude-code + codex
  install    Sync repo → local ~/.claude/skills
  all        Run platforms then install

Usage:
  python skill_sync.py platforms
  python skill_sync.py all --dry-run
"""
import argparse
import hashlib
import shutil
import sys
from pathlib import Path

CANON_DIR = 'skills'                    # Canonical source
PLATFORMS = ['claude-code', 'codex']    # Derived platform distributions

SYNC_ITEMS = ['SKILL.md', 'resources', 'scripts', 'requirements.txt', 'tests']

EXCLUDE_DIRS = {'__pycache__', 'venv', '.git'}
EXCLUDE_EXTS = {'.pyc', '.pyo'}

SKILLS = [
    ('vedic-reader',     'vedic-reader',     'shared'),
    ('vedic-career',     'vedic-career',     'shared'),
    ('vedic-love',       'vedic-love',       'shared'),
    ('vedic-synastry',   'vedic-synastry',   'shared'),
    ('vedic-rectifier',  'vedic-rectifier',  'shared'),
    ('vedic-prashna',    'vedic-prashna',    'shared'),
    ('vedic-calculator', 'vedic-calculator', 'shared'),
    ('vedic-core',       'vedic-core',       'open'),
    ('vedic-core',       'vedic-core-pro',   'pro'),
]

INSTALL_ROOTS = [
    ('claude', Path.home() / '.claude' / 'skills'),
    ('antigravity', Path.home() / '.gemini' / 'config' / 'skills'),
]


def sha(p: Path) -> str:
    return hashlib.sha1(p.read_bytes()).hexdigest()


def iter_files(root: Path):
    """Enumerate files to be synced under root, applying exclusions."""
    if not root.exists():
        return
    for p in root.rglob('*'):
        if not p.is_file():
            continue
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        if p.suffix in EXCLUDE_EXTS:
            continue
        yield p.relative_to(root)


def copy_one(s: Path, d: Path, label: str, dry: bool) -> int:
    if d.exists() and sha(s) == sha(d):
        return 0
    print(f'  [{"DIFF" if dry else "SYNC"}] {label}')
    if not dry:
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(s, d)
    return 1


def sync_skill(src: Path, dst: Path, label: str, dry: bool) -> int:
    """Sync src to dst per SYNC_ITEMS, returns count of modified files."""
    n = 0
    for item in SYNC_ITEMS:
        s = src / item
        if not s.exists():
            continue
        if s.is_dir():
            for rel in iter_files(s):
                n += copy_one(s / rel, dst / item / rel, f'{label}/{item}/{rel}', dry)
        else:
            n += copy_one(s, dst / item, f'{label}/{item}', dry)
    return n


def find_orphans(src: Path, dst: Path, label: str):
    """Find files present in dst but absent from src."""
    out = []
    for item in SYNC_ITEMS:
        s, d = src / item, dst / item
        if not d.exists() or not d.is_dir():
            continue
        have = set(iter_files(s)) if s.exists() else set()
        for rel in iter_files(d):
            if rel not in have:
                out.append((f'{label}/{item}/{rel}', d / rel))
    return out


def cmd_platforms(repos, dry: bool) -> int:
    total = 0
    for label, repo in repos:
        canon = repo / CANON_DIR
        if not canon.exists():
            print(f'  [SKIP] {label}: Missing {CANON_DIR}/')
            continue
        for name in sorted(d.name for d in canon.iterdir() if d.is_dir()):
            for plat in PLATFORMS:
                total += sync_skill(canon / name, repo / plat / 'skills' / name,
                                    f'{label}/{plat}/{name}', dry)
    return total


def cmd_install(repo_open: Path, repo_pro: Path, dry: bool, prune: bool) -> int:
    total = 0
    orphans = []
    for src_name, dst_name, kind in SKILLS:
        repo = repo_pro if kind == 'pro' else repo_open
        if repo is None or not repo.exists():
            print(f'  [SKIP] {dst_name}: Repository unavailable')
            continue
        src = repo / CANON_DIR / src_name
        if not src.exists():
            print(f'  [SKIP] {dst_name}: {src} does not exist')
            continue
        for root_label, root in INSTALL_ROOTS:
            dst = root / dst_name
            total += sync_skill(src, dst, f'{root_label}/{dst_name}', dry)
            orphans += find_orphans(src, dst, f'{root_label}/{dst_name}')

    if orphans:
        print(f'\n  ── Local orphan files not in repo ({len(orphans)}) ──')
        for label, path in orphans:
            print(f'  [ORPHAN] {label}')
            if prune and not dry:
                path.unlink()
                print('           ^ Removed (--prune)')
        if not prune:
            print('  (Report only; use --prune to clean up)')
    return total


def check_shared_parity(repo_open: Path, repo_pro: Path):
    if repo_pro is None or not repo_pro.exists():
        return
    for src_name, _, kind in SKILLS:
        if kind != 'shared':
            continue
        a = repo_open / CANON_DIR / src_name
        b = repo_pro / CANON_DIR / src_name
        if not a.exists() or not b.exists():
            continue
        for rel in iter_files(a):
            fb = b / rel
            if not fb.exists() or sha(a / rel) != sha(fb):
                print(f'  [WARN] Parity mismatch between repositories: {src_name}/{rel}')


def main():
    ap = argparse.ArgumentParser(description='Repo to platform copies synchronizer')
    ap.add_argument('cmd', choices=['platforms', 'install', 'all'])
    ap.add_argument('--pro', help='Pro repo path')
    ap.add_argument('--dry-run', action='store_true', help='Report differences without modifying files')
    ap.add_argument('--prune', action='store_true', help='Remove orphaned files during install')
    args = ap.parse_args()

    repo_open = Path(__file__).resolve().parent
    repo_pro = Path(args.pro) if args.pro else repo_open.parent / 'vedic-astro-skills-pro'
    if not repo_pro.exists():
        repo_pro = None

    print(f'\n{"=" * 46}')
    print(f'  skill_sync · {args.cmd}{"  [DRY RUN]" if args.dry_run else ""}')
    print(f'  Open Repo: {repo_open}')
    print(f'  Pro Repo:  {repo_pro if repo_pro else "(none)"}')
    print(f'{"=" * 46}\n')

    repos = [('OS', repo_open)] + ([('Pro', repo_pro)] if repo_pro else [])
    total = 0

    if args.cmd in ('platforms', 'all'):
        print('── Synchronizing platform copies ──')
        total += cmd_platforms(repos, args.dry_run)

    if args.cmd in ('install', 'all'):
        print('\n── Installing locally ──')
        check_shared_parity(repo_open, repo_pro)
        total += cmd_install(repo_open, repo_pro, args.dry_run, args.prune)

    if total == 0:
        print('\n  All endpoints in sync, no changes needed')
    print(f'\nDone ({"Pending" if args.dry_run else "Synchronized"} {total} files)\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
