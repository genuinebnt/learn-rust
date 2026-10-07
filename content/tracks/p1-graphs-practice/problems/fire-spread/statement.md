A forest plan is a list of strings: `.` is grass, `#` is bare rock (fire cannot cross it) and `F` is a fire. Every minute, each fire spreads to the grass tiles directly up, down, left and right of it.

Return the number of minutes until **all the grass is burning**. Return `0` if there is no grass, and `-1` if some grass can never catch fire.

```python
minutes_to_burn([
    "F..",
    "...",
    "..F",
])  # 2
```
