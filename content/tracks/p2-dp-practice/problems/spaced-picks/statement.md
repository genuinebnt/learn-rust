Prizes are lined up with values `values`. You may pick any prizes, but any two you pick must be at least `gap` positions apart (`gap = 1` means no limit; `gap = 2` means no two neighbours, like robbing houses). Return the largest total value you can pick.

```python
best_picks([3, 2, 7, 10], 2)       # 13: 3 + 10
best_picks([4, 1, 1, 9, 1], 3)     # 13: 4 + 9
```

Values are not negative. Return `0` for an empty list.
