from collections import Counter


def deletions_to_match(a: str, b: str) -> int:
    ca, cb = Counter(a), Counter(b)
    return sum((ca - cb).values()) + sum((cb - ca).values())
