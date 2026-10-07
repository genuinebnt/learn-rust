A river has `stones` stepping stones numbered `1` to `stones` in a row. You stand on the bank, which counts as stone `0`. In one hop you can move forward **1, 2 or 3** stones. How many different sequences of hops take you from the bank exactly onto the last stone?

```python
hop_ways(3)   # 4: (1,1,1) (1,2) (2,1) (3)
hop_ways(4)   # 7
hop_ways(0)   # 1: you are already there
```

`stones` can be up to 60, so counting by trying every sequence is too slow.
