def build_order(n: int, needs: list[tuple[int, int]]) -> list[int] | None:
    waiting_on = [[] for _ in range(n)]
    for package, need in needs:
        waiting_on[need].append(package)
    seen, order = set(), []

    def visit(p):
        if p in seen:
            return
        seen.add(p)
        for q in waiting_on[p]:
            visit(q)
        order.append(p)

    for p in range(n):
        visit(p)
    return order[::-1]
