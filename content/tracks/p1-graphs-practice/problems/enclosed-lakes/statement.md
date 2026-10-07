A map is a list of strings: `~` is water and `.` is land. Water tiles that touch up, down, left or right belong to the same body of water. A body of water that touches the **edge of the map**, directly or through other water, drains away. Any other body of water is an **enclosed lake**.

Return how many water tiles are in enclosed lakes.

```python
enclosed_lake_tiles([
    "~~~~~",
    "~...~",
    "~.~.~",
    "~...~",
    "~~~~~",
])  # 1
```
