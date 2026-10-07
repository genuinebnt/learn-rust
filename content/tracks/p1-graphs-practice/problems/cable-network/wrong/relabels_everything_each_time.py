def networks_after_each_cable(n: int, cables: list[tuple[int, int]]) -> list[int]:
    comp = list(range(n))
    out = []
    for a, b in cables:
        ca, cb = comp[a], comp[b]
        comp = [ca if c == cb else c for c in comp]
        out.append(len(set(comp)))
    return out
