def best_profit_with_fee(prices: list[int], fee: int) -> int:
    return sum(max(0, b - a - fee) for a, b in zip(prices, prices[1:]))
