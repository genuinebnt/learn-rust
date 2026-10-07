A road has toll stops numbered `0` to `n - 1`, each with a toll. Your trip starts at stop `0`. From any stop you can drive **1, 2 or 3** stops ahead. You pay the toll of every stop you land on, including stop `0`. The trip is over once you drive **past the last stop**.

Return the smallest total toll. With no stops, the trip costs `0`.

```python
cheapest_trip([5, 1, 1, 9, 1])   # 6: stops 0 and 2, then drive 3 stops past the end
cheapest_trip([4, 7, 2])         # 4: stop 0, then drive 3 stops, past the end
```
