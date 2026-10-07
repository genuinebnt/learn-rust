An office has `n` computers numbered `0` to `n - 1`, with no cables. Cables are plugged in one at a time; a cable `(a, b)` connects computers `a` and `b` in both directions. Computers joined by cables, directly or through other computers, are on the same **network**.

Return a list with the number of separate networks after each cable is plugged in (so it has one number per cable).

```python
networks_after_each_cable(4, [(0, 1), (2, 3), (1, 2), (0, 3)])  # [3, 2, 1, 1]
```

The last cable joins two computers that were already connected, so the count stays at 1.
