import random

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


def test_a_longer_cycle_is_returned_in_import_order():
    imports = {"a": ["b"], "b": ["c"], "c": ["d"], "d": ["b"]}
    got = find_import_cycle(imports)
    ensure(got is not None and is_cycle(imports, got), f"got {got}")
    check("modules on the cycle", sorted(got), ["b", "c", "d"])


def test_a_cycle_not_reachable_from_the_first_module():
    imports = {"a": [], "b": ["c"], "c": ["b"]}
    got = find_import_cycle(imports)
    ensure(got is not None and is_cycle(imports, got), f"got {got}")


def test_the_returned_modules_are_only_the_cycle():
    imports = {"app": ["x", "y"], "x": ["y"], "y": ["z"], "z": ["x"]}
    got = find_import_cycle(imports)
    ensure(got is not None and is_cycle(imports, got), f"got {got}")
    ensure("app" not in got, "app only reaches the cycle, it is not on it")


def test_modules_missing_as_keys_import_nothing():
    check('find_import_cycle({"a": ["ghost"]})', find_import_cycle({"a": ["ghost"]}), None)


def test_a_finished_module_is_not_searched_again():
    imports = {f"m{i}": [f"m{i + 1}", f"m{i + 2}"] for i in range(2000)}
    check("find_import_cycle(a wide acyclic chain of 2000)", find_import_cycle(imports), None)


def test_a_deep_chain_that_ends_in_a_cycle():
    imports = {f"m{i}": [f"m{i + 1}"] for i in range(5000)}
    imports["m4999"] = ["m4998"]
    got = find_import_cycle(imports)
    ensure(got is not None and is_cycle(imports, got), "expected the two-module cycle at the end of the chain")
    check("modules on the cycle", sorted(got), ["m4998", "m4999"])


def test_two_separate_cycles():
    imports = {"a": ["b"], "b": ["a"], "c": ["d"], "d": ["c"]}
    got = find_import_cycle(imports)
    ensure(got is not None and is_cycle(imports, got), f"got {got}")


def test_random_graphs_against_a_reachability_check():
    rng = random.Random(17)
    for _ in range(300):
        names = [chr(97 + i) for i in range(rng.randint(1, 6))]
        imports = {n: [rng.choice(names) for _ in range(rng.randint(0, 2))] for n in names}
        got = find_import_cycle(imports)
        if has_cycle(imports):
            ensure(got is not None and is_cycle(imports, got), f"{imports} has a cycle; got {got}")
        else:
            check(f"find_import_cycle({imports})", got, None)
