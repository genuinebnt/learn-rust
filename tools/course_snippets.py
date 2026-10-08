#!/usr/bin/env python3
"""Compile and run the code in the course's concept articles.

A concept's fenced block whose info string is `rust test` is real code: this tool puts each concept's blocks into a module of a scratch
crate and runs `cargo test`, so every example a learner reads has been compiled and its `assert_eq!`s have held. Blocks marked just `rust`
are illustrations and are not run.

Usage: tools/course_snippets.py [courses/bustub/concepts] [--keep]
"""
import glob, os, re, subprocess, sys, tempfile

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    root = args[0] if args else 'courses/bustub/concepts'
    work = os.path.join(tempfile.gettempdir(), 'anneal-concept-snippets')
    os.makedirs(work + '/src', exist_ok=True)
    open(work + '/Cargo.toml', 'w').write('[package]\nname = "snips"\nversion = "0.1.0"\nedition = "2021"\n\n[workspace]\n\n[dependencies]\n')
    mods, total = [], 0
    for old in glob.glob(work + '/src/*.rs'):
        os.remove(old)
    for md in sorted(glob.glob(root + '/*.md')):
        name = re.sub(r'\W', '_', os.path.basename(md)[:-3])
        text = open(md).read()
        blocks = re.findall(r'^```rust test[^\n]*\n(.*?)^```', text, re.S | re.M)
        if not blocks:
            continue
        total += len(blocks)
        body = '\n\n'.join(f'mod b{i} {{\n#![allow(unused)]\n{b}\n}}' for i, b in enumerate(blocks))
        open(f'{work}/src/{name}.rs', 'w').write('#![allow(unused)]\n' + body)
        mods.append(name)
    open(work + '/src/lib.rs', 'w').write('#![allow(unused)]\n' + ''.join(f'mod {m};\n' for m in mods))
    print(f'{total} runnable blocks in {len(mods)} concepts')
    r = subprocess.run(['cargo', 'test', '--quiet', '--manifest-path', work + '/Cargo.toml'], capture_output=True, text=True)
    out = r.stdout + r.stderr
    errs = [l for l in out.splitlines() if l.startswith('error') or 'panicked' in l or l.startswith('---- ') or 'FAILED' in l]
    print('\n'.join(errs[:40]) if errs else '', flush=True)
    summ = [l for l in out.splitlines() if l.startswith('test result')]
    print('\n'.join(summ))
    if r.returncode != 0:
        print(out[-3000:])
    return r.returncode

if __name__ == '__main__':
    sys.exit(main())
