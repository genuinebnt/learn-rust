A till holds bills of several kinds, given as `(value, how_many)` pairs. Pay `amount` **exactly** using the **fewest bills**, never using more of a kind than the till has. Return the number of bills, or `-1` if the amount can't be made.

```python
fewest_bills([(1, 5), (5, 2), (10, 1)], 18)   # 5: 10 + 5 + 1 + 1 + 1
fewest_bills([(5, 1)], 10)                    # -1: only one 5
fewest_bills([(4, 3), (3, 3)], 6)             # 2: 3 + 3
```
