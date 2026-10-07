def networks_after_each_cable(n: int, cables: list[tuple[int, int]]) -> list[int]:
    parent = list(range(n))
    size = [1] * n

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    networks = n
    counts = []
    for a, b in cables:
        ra, rb = find(a), find(b)
        if ra != rb:
            if size[ra] < size[rb]:
                ra, rb = rb, ra
            parent[rb] = ra
            size[ra] += size[rb]
            networks -= 1
        counts.append(networks)
    return counts
