def deletions_to_match(a: str, b: str) -> int:
    previous = [0] * (len(b) + 1)
    for ch in a:
        current = [0]
        for j, other in enumerate(b, start=1):
            if ch == other:
                current.append(previous[j - 1] + 1)
            else:
                current.append(max(previous[j], current[j - 1]))
        previous = current
    return len(a) + len(b) - 2 * previous[-1]
