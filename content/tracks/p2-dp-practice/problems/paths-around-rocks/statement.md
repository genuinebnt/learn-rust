A hiking map is a list of strings: `.` is open ground and `#` is a rock you can't step on. Starting in the **top-left** corner you may only move **right** or **down**. Return the number of different routes to the **bottom-right** corner.

```python
count_paths([
    "...",
    ".#.",
    "...",
])  # 2
```

If the start or the finish is a rock there are no routes (`0`), and so for an empty map.
