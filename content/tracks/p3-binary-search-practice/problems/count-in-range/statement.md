`values` is sorted in increasing order (duplicates allowed) and can be **enormous**: the tests pass a list of hundreds of millions of numbers, so you can't look at each one. Return how many values `v` satisfy `low <= v <= high`.

```python
count_in_range([1, 2, 2, 2, 5, 9], 2, 5)    # 4
count_in_range([1, 2, 3], 10, 20)           # 0
count_in_range([1, 2, 3], 3, 1)             # 0
```
