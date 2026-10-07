Builds are numbered `1` to `n`. Some build introduced a bug, and every later build has it too, so `is_bad(build)` is `False` for the first few builds and then `True` for all the rest. Testing a build is slow, so call `is_bad` as few times as you can.

Return the number of the **first bad build**, or `-1` if no build is bad.

```python
first_bad_build(10, lambda b: b >= 7)    # 7
first_bad_build(5, lambda b: False)      # -1
```

`n` can be up to 10^9. The tests check how many times you call `is_bad`.
