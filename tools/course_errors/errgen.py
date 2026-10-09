"""Generates courses/bustub/concepts/errors-<module>.md. Run errcheck.py first (it compiles every snippet with rustc and saves the messages), then errgen.py.
Add a family in errfam.py, a module line in errmods.py."""
import os, sys, json, re, os, tomllib, glob
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from errfam import FAM
from errmods import MODS
msgs=json.load(open("/tmp/course-errors/messages.json"))
BASE=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","..","courses","bustub")
titles={}
for f in glob.glob(BASE+"/modules/*/module.toml"):
    t=tomllib.load(open(f,"rb")); titles[t["code"]]=t["title"]
import textwrap
def clean(m):
    m=re.sub(r"--> /[^\s:]*/([A-Za-z_0-9]+)\.rs:", "--> src/main.rs:", m)
    # rustc prints the headline as one long line: wrap it (and `help`/`note` lines) so it can be read without scrolling
    out=[]
    for l in m.splitlines():
        if re.match(r"(error|warning|help|note)(\[E\d+\])?:", l) and len(l) > 86:
            out.extend(textwrap.wrap(l, 86, subsequent_indent="    "))
        else:
            out.append(l)
    return "\n".join(out)
os.makedirs(BASE+"/concepts",exist_ok=True)
for code, items in MODS.items():
    if code not in titles: print("no module",code); continue
    parts=[]
    parts.append(f"---\ntitle: Errors you will meet: {titles[code]}\nsummary: The compiler messages this module is most likely to provoke, what each one means in plain words, and the usual ways out.\nminutes: {2+len(items)*2}\n---\n")
    parts.append("Compiler errors are the course's second teacher. These are the ones this module's designs tend to provoke. Each shows the message as `rustc` prints it (read it from the top: the first line says what, the arrows say where, the `help:` line often says how), what it means, where you will probably meet it here, and the usual fixes. The messages and the fixes on this page were produced and checked with a real compiler.\n")
    for fid, where in items:
        f=FAM[fid]
        parts.append(f"## {f['code']}: {f['title']}\n")
        parts.append(f"**Where you will meet it here.** {where}\n")
        parts.append("**A small program that does it:**\n\n```rust\n"+f["bad"]+"\n```\n")
        parts.append("**What the compiler says:**\n\n```text\n"+clean(msgs[fid])+"\n```\n")
        parts.append("**What it means.** "+f["meaning"]+"\n")
        parts.append("**The usual ways out:**\n\n"+"\n".join("- "+x for x in f["fixes"])+"\n")
        parts.append("**One fix, compiled and checked:**\n\n```rust\n"+f["good"]+"\n```\n")
    open(f"{BASE}/concepts/errors-{code}.md","w").write("\n".join(parts))
print("pages:",len(MODS))
