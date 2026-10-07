Write a `Ledger` that records transactions and answers balance questions.

- `add(day, amount)` records a transaction. Days are **strictly increasing** across calls.
- `balance_on(day)` returns the total of every amount recorded on a day `<= day`, or `0` if there are none.

```python
ledger = Ledger()
ledger.add(3, 100)
ledger.add(7, -40)
ledger.balance_on(5)    # 100
ledger.balance_on(7)    # 60
ledger.balance_on(2)    # 0
```

There can be 100,000 transactions and 100,000 questions.
