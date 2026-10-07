"""Helper used while authoring: append techniques to a pattern in techniques.py. Usage: addtech.py <json file>"""
import json, sys
p = "tools/neetcode/techniques.py"
s = open(p).read()
for pattern, items in json.load(open(sys.argv[1])).items():
    i = s.index(f'    "{pattern}": [\n')
    j = s.index('    ],\n', i)
    block = s[i:j]
    new = "".join(f'        ("{k}", "{n}"),\n' for k, n in items if f'("{k}",' not in block)
    s = s[:j] + new + s[j:]
open(p, "w").write(s)
