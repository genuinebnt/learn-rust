import subprocess, tempfile, os, re, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from errfam import FAM
out = {}
d = tempfile.mkdtemp()
def compile_(src, name):
    p = os.path.join(d, name + ".rs")
    open(p, "w").write(src + "\n")
    r = subprocess.run(["rustc", "--edition", "2021", "--crate-type", "bin", "-A", "warnings", "--color", "never", "-o", os.path.join(d, name), p], capture_output=True, text=True)
    return r.returncode, r.stderr
bad_ok = True
for k, f in FAM.items():
    rc, err = compile_(f["bad"], k + "_bad")
    if rc == 0 or ("error[" + f["code"] + "]") not in err and f["code"] != "E0432":
        print("BAD snippet does not give", f["code"], "->", k, err[:300]); bad_ok = False
    if k == "unresolved" and "E0432" not in err and "E0433" not in err:
        print("unresolved import did not fail with E0432/E0433:", err[:200]); bad_ok = False
    rc2, err2 = compile_(f["good"], k + "_good")
    if rc2 != 0:
        print("GOOD snippet fails ->", k, err2[:400]); bad_ok = False
    # keep the message: from the first 'error' line to the end of the first diagnostic
    lines = err.splitlines()
    msg = []
    for l in lines:
        if l.startswith("error: aborting") or l.startswith("error: could not compile") or l.startswith("For more information"):
            break
        msg.append(l)
    out[k] = "\n".join(msg).strip()
os.makedirs("/tmp/course-errors", exist_ok=True)
json.dump(out, open("/tmp/course-errors/messages.json", "w"), indent=1)
print("families:", len(FAM), "all ok" if bad_ok else "PROBLEMS")
