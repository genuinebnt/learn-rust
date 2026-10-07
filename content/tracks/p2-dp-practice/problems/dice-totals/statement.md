Roll `dice` dice, each with faces numbered `1` to `faces`. Return the number of **different outcomes** (the order of the dice matters, so `1+2` and `2+1` count separately) whose faces add up to exactly `total`.

```python
dice_ways(2, 6, 7)    # 6
dice_ways(1, 6, 7)    # 0
dice_ways(0, 6, 0)    # 1
```
