`schedule[e]` lists employee `e`'s working intervals `(start, end)`, sorted and not overlapping; each
covers the time from `start` up to but not including `end`. Return the free time every employee shares:
the gaps of positive length between the first start and the last end, sorted.
