A picture is a grid of colour numbers. `paint_region(picture, row, col, colour)` works like the paint bucket in a drawing program: it recolours the clicked cell and every cell connected to it (up, down, left, right) that has the **same colour as the clicked cell**.

Return the new picture. **Don't change the picture you were given.**

```python
paint_region([[1, 1, 0],
              [1, 0, 0],
              [1, 1, 1]], 0, 0, 7)
# [[7, 7, 0],
#  [7, 0, 0],
#  [7, 7, 7]]
```
