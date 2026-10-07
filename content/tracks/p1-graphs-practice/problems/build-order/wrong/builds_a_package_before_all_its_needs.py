from collections import deque


def build_order(n: int, needs: list[tuple[int, int]]) -> list[int] | None:
    waiting_on = [[] for _ in range(n)]
    seen_needs = [False] * n
    for package, need in needs:
        waiting_on[need].append(package)
        seen_needs[package] = True
    ready = deque(p for p in range(n) if not seen_needs[p])
    order, done = [], set()
    while ready:
        package = ready.popleft()
        if package in done:
            continue
        done.add(package)
        order.append(package)
        for dependant in waiting_on[package]:
            ready.append(dependant)
    return order if len(order) == n else None
