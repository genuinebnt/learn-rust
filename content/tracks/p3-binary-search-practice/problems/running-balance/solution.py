from bisect import bisect_right


class Ledger:
    def __init__(self):
        self.days = []
        self.totals = []  # totals[i]: the balance after the i-th transaction

    def add(self, day: int, amount: int) -> None:
        self.days.append(day)
        self.totals.append((self.totals[-1] if self.totals else 0) + amount)

    def balance_on(self, day: int) -> int:
        i = bisect_right(self.days, day)
        return self.totals[i - 1] if i else 0
