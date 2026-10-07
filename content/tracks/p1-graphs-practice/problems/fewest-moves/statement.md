A knight moves on a chessboard in an "L": two squares in one direction and one square sideways (8 possible jumps, minus the ones that leave the board).

`fewest_knight_moves(start, goal, size)` returns the **fewest moves** a knight needs to get from `start` to `goal` on a `size × size` board, where squares are `(row, col)` from `(0, 0)`. Return `-1` if the goal can't be reached (this only happens on tiny boards).

```python
fewest_knight_moves((0, 0), (1, 2), 8)   # 1
fewest_knight_moves((0, 0), (7, 7), 8)   # 6
```

The board can be up to 200 × 200.
