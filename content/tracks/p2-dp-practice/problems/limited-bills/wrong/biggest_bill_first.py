def fewest_bills(bills: list[tuple[int, int]], amount: int) -> int:
    used = 0
    for value, count in sorted(bills, reverse=True):
        take = min(count, amount // value)
        amount -= take * value
        used += take
    return used if amount == 0 else -1
