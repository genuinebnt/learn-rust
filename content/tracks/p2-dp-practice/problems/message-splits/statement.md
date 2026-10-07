A message is a string of digits. Cut it into **pieces**, in order, where every piece is a number from `1` to `biggest` written **without a leading zero** (so `"05"` is not a piece, but `"5"` and `"50"` are). Return how many different ways there are to cut the whole message.

```python
count_splits("123", 26)    # 3: 1|2|3, 12|3, 1|23
count_splits("100", 100)   # 1: only "100"; "1|00" and "10|0" use pieces starting with 0
count_splits("", 9)        # 1: the empty message has one (empty) split
```

Return `0` if the message can't be cut at all.
