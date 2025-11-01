#!/usr/bin/env python3
"""
audit_featured_images.py
Scan Jekyll posts in ./_posts, validate `featured_image` (or `hero_image`) paths,
and report any missing files, case mismatches, or extension issues.

USAGE:
  python3 audit_featured_images.py
  python3 audit_featured_images.py --root /path/to/your/jekyll/repo

It prints a summary table and writes a CSV report to:
  ./featured_image_audit.csv

Return code is non-zero if any issues are found.
"""

import os
import sys
import argparse
import csv

def read_front_matter(path):
    """Return (front_matter_dict, body_str). Lightweight parser for YAML-like header.
    We only care about lines like: key: value
    """
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()

    fm = {}
    body_start = 0
    if len(lines) >= 1 and lines[0].strip() == '---':
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                body_start = i + 1
                for line in lines[1:i]:
                    if ':' in line:
                        key, val = line.split(':', 1)
                        fm[key.strip()] = val.strip().strip('"').strip("'")
                break
    body = '\n'.join(lines[body_start:])
    return fm, body

def case_insensitive_lookup(root, rel_path):
    rel = rel_path.lstrip('/').replace('\\', '/')
    parts = rel.split('/')
    cur = root
    built = []
    for part in parts:
        try:
            entries = os.listdir(cur)
        except FileNotFoundError:
            return None
        if part in entries:
            cur = os.path.join(cur, part)
            built.append(part)
            continue
        lower_map = {e.lower(): e for e in entries}
        if part.lower() in lower_map:
            real = lower_map[part.lower()]
            cur = os.path.join(cur, real)
            built.append(real)
        else:
            return None
    return '/'.join(built)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.', help='Repo root (default: current directory)')
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    posts_dir = os.path.join(root, '_posts')
    if not os.path.isdir(posts_dir):
        print(f'ERROR: Not a Jekyll repo root? Missing directory: {posts_dir}', file=sys.stderr)
        sys.exit(2)

    rows = []
    issues = 0

    for name in sorted(os.listdir(posts_dir)):
        if not (name.endswith('.md') or name.endswith('.markdown')):
            continue
        post_path = os.path.join(posts_dir, name)
        fm, _ = read_front_matter(post_path)

        img = fm.get('featured_image') or fm.get('hero_image') or ''
        img = img.strip()

        status = 'OK'
        suggested = ''
        exists_exact = False
        exists_any_case = False

        if img:
            rel = img.lstrip('/').replace('\\','/')
            abs_img = os.path.join(root, rel)
            if os.path.isfile(abs_img):
                exists_exact = True
            else:
                corrected = case_insensitive_lookup(root, img)
                if corrected:
                    exists_any_case = True
                    suggested = '/' + corrected
                    status = 'Case mismatch (suggest fix)'
                    issues += 1
                else:
                    status = 'Missing file'
                    issues += 1
        else:
            status = 'No featured_image (or hero_image) in front matter'
            issues += 1

        rows.append({
            'post_file': f'_posts/{name}',
            'featured_image': img,
            'exists_exact': 'yes' if exists_exact else 'no',
            'exists_any_case': 'yes' if exists_any_case else 'no',
            'suggested_path': suggested,
            'status': status,
        })

    print('\nFeatured Image Audit\n' + '='*80)
    for r in rows:
        print(f"{r['post_file']:<45}  {r['featured_image']:<50}  {r['status']}")
        if r['suggested_path']:
            print(f"{'':<47}suggested: {r['suggested_path']}")

    out_csv = os.path.join(root, 'featured_image_audit.csv')
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else
                           ['post_file','featured_image','exists_exact','exists_any_case','suggested_path','status'])
        w.writeheader()
        w.writerows(rows)

    print('\nWrote report:', out_csv)
    if issues:
        print(f'Found {issues} issue(s).')
        sys.exit(1)
    else:
        print('All good.')
        sys.exit(0)

if __name__ == '__main__':
    main()
