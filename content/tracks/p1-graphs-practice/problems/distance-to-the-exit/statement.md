A building plan is a list of strings: `#` is a wall, `.` is floor, and `E` is an exit. You can walk up, down, left or right through floor and exit tiles.

Return a grid of the same size where each floor tile holds the number of steps to its **nearest exit**. Exits hold `0`. Walls hold `-1`, and so do floor tiles from which no exit can be reached.

```python
distance_to_exit([
    "E..",
    ".#.",
    "..E",
])
# [[0, 1, 2],
#  [1, -1, 1],
#  [2, 1, 0]]
```

The plan can be up to 150 × 150, so searching from every tile separately is too slow.
