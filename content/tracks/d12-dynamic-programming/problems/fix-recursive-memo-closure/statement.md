`climb_ways(n)` should count the ways to climb `n` stairs taking 1, 2 or 3 steps at a time,
memoising in a `HashMap`. It doesn't compile: the closure passed to `or_insert_with` needs
`memo` while `entry` is still holding it (E0500). Fix it and keep the memo.
