def best_profit_with_fee(prices: list[int], fee: int) -> int:
    if not prices:
        return 0
    cash, hold = 0, -prices[0] - fee
    for price in prices[1:]:
        cash, hold = max(cash, hold + price - fee), max(hold, cash - price - fee)
    return cash
