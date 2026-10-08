#!/usr/bin/env python3
"""Shorten the `### Tests` bullets of merged stages to the standard (docs/COURSE_STANDARDS.md): at most 4 per block, 8 per stage.

Adjacent bullets of a block are joined; if a stage still has more than 8, each block is reduced to one bullet.
Usage: tools/course_condense_tests.py courses/bustub/modules [stage ids...]
"""
import glob, re, sys

def blocks_of(lines):
    out = []
    fence = False
    for i, l in enumerate(lines):
        if l.strip().startswith('```'):
            fence = not fence
        if not fence and re.match(r'#{2,3} Tests\s*$', l):
            j, idx = i + 1, []
            while j < len(lines) and not re.match(r'#{1,3} ', lines[j]):
                if lines[j].startswith('- '):
                    idx.append(j)
                j += 1
            out.append(idx)
    return out

def join(lines, idx, parts):
    items = []
    for k in idx:
        items.append(lines[k][2:].rstrip())
    per = max(1, -(-len(items) // parts))
    groups = [items[i:i + per] for i in range(0, len(items), per)]
    new = ['- ' + ' '.join(x if x.endswith(('.', ':', ';')) else x + '.' for x in g) for g in groups]
    # replace: first bullet line gets all groups (as separate lines), delete the rest
    for k in reversed(idx[1:]):
        del lines[k]
    lines[idx[0]:idx[0] + 1] = new

def process(md):
    lines = md.split('\n')
    for blk in reversed(blocks_of(lines)):
        if len(blk) > 2:
            join(lines, blk, 2)
    total = sum(len(b) for b in blocks_of(lines))
    if total > 8:
        for blk in reversed(blocks_of(lines)):
            if len(blk) > 1:
                join(lines, blk, 1)
    return '\n'.join(lines)

if __name__ == '__main__':
    root = sys.argv[1]
    n = 0
    for p in glob.glob(f'{root}/*/stages/*/stage.md'):
        s = open(p).read()
        t = process(s)
        if t != s:
            open(p, 'w').write(t)
            n += 1
    print(n, 'stages condensed')
