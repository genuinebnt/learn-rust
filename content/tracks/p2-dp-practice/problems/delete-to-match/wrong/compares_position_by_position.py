def deletions_to_match(a: str, b: str) -> int:
    same = sum(1 for x, y in zip(a, b) if x == y)
    return len(a) + len(b) - 2 * same
