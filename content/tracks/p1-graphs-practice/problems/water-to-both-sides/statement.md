A heightmap is a grid of heights. Rain on a cell flows to any neighbour (up, down, left, right) that is **as high or lower**, and keeps flowing. The **west coast** is the left column and the **east coast** is the right column: water in a coast column has reached that coast.

Return the `(row, col)` of every cell whose water can reach **both** coasts, sorted by row and then column.

```python
drains_to_both([[1, 2, 1],
                [3, 1, 3]])
# [(0, 1)]
```
