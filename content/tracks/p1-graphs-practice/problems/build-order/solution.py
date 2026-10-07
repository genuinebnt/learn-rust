from collections import deque


def build_order(n: int, needs: list[tuple[int, int]]) -> list[int] | None:
    waiting_on = [[] for _ in range(n)]
    missing = [0] * n
    for package, need in needs:
        waiting_on[need].append(package)
        missing[package] += 1
    ready = deque(p for p in range(n) if missing[p] == 0)
    order = []
    while ready:
        package = ready.popleft()
        order.append(package)
        for dependant in waiting_on[package]:
            missing[dependant] -= 1
            if missing[dependant] == 0:
                ready.append(dependant)
    return order if len(order) == n else None
