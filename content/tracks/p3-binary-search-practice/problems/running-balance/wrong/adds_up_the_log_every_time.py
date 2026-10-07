class Ledger:
    def __init__(self):
        self.entries = []

    def add(self, day: int, amount: int) -> None:
        self.entries.append((day, amount))

    def balance_on(self, day: int) -> int:
        return sum(amount for d, amount in self.entries if d <= day)
