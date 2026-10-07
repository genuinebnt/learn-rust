Boxes are given as `(width, height)` pairs. One box fits **inside** another if both its width and its height are **strictly smaller** (no rotating). Return the length of the longest chain of boxes `b1 ⊂ b2 ⊂ b3 ⊂ …`, each inside the next.

```python
longest_nesting([(5, 4), (6, 4), (6, 7), (2, 3)])   # 3: (2,3) in (5,4) in (6,7)
longest_nesting([(2, 2), (2, 2)])                   # 1
```

There can be up to 100,000 boxes.
