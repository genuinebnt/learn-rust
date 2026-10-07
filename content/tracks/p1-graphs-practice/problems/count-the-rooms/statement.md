A floor plan is a list of strings. `#` is a wall and `.` is floor. A **room** is a group of floor tiles that touch each other up, down, left or right (not diagonally). Return how many rooms the plan has.

```python
count_rooms([
    "..#..",
    "..#..",
    "###..",
])  # 2
```

- Rows all have the same length; the plan can be empty.
- The plan can be up to 300 × 300.
