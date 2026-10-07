Cut a list of non-negative numbers into **exactly** `parts` consecutive pieces (no piece may be empty; `1 <= parts <= len(values)`). The cost of a cutting is the **largest piece sum**. Return the smallest cost over all ways to cut.

```python
fair_split([7, 2, 5, 10, 8], 2)    # 18: [7, 2, 5] and [10, 8]
fair_split([1, 2, 3, 4, 5], 3)     # 6
fair_split([4, 4, 4], 3)           # 4
```
