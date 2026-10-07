from anneal_prelude import check, ensure
from solution import find_import_cycle

def is_cycle(imports, cycle):
    """Whether `cycle` is a real loop: each module imports the next, and the last imports the first."""
    if not cycle:
        return False
    return all(cycle[(i + 1) % len(cycle)] in imports.get(m, []) for i, m in enumerate(cycle)) and len(set(cycle)) == len(cycle)


def has_cycle(imports):
    names = set(imports) | {m for ms in imports.values() for m in ms}
    reach = {a: set(imports.get(a, [])) for a in names}
    changed = True
    while changed:
        changed = False
        for a in names:
            new = set().union(*(reach[b] for b in reach[a])) | reach[a] if reach[a] else reach[a]
            if new != reach[a]:
                reach[a] = new
                changed = True
    return any(a in reach[a] for a in names)


def test_a_two_module_cycle():
    imports = {"app": ["db", "log"], "db": ["log"], "log": ["db"]}
    got = find_import_cycle(imports)
    ensure(got is not None and is_cycle(imports, got), f"expected a cycle between db and log, got {got}")
    check("modules on the cycle", sorted(got), ["db", "log"])


def test_no_cycle():
    check('find_import_cycle({"a": ["b"], "b": []})', find_import_cycle({"a": ["b"], "b": []}), None)


def test_a_module_importing_itself():
    check('find_import_cycle({"a": ["a"]})', find_import_cycle({"a": ["a"]}), ["a"])


def test_no_modules():
    check("find_import_cycle({})", find_import_cycle({}), None)


def test_a_diamond_is_not_a_cycle():
    imports = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}
    check("find_import_cycle(a diamond)", find_import_cycle(imports), None)
