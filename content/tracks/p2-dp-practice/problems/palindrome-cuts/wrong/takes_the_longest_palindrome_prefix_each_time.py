def fewest_cuts(s: str) -> int:
    cuts, i = 0, 0
    while i < len(s):
        j = len(s)
        while j > i and s[i:j] != s[i:j][::-1]:
            j -= 1
        i = j
        if i < len(s):
            cuts += 1
    return cuts
