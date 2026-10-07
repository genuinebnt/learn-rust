def kth_of_two(a: list[int], b: list[int], k: int) -> int:
    i = min(len(a), k // 2)
    j = min(len(b), k - i)
    return max(a[i - 1] if i else float("-inf"), b[j - 1] if j else float("-inf"))
