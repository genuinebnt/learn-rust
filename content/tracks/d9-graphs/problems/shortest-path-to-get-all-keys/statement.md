`grid` rows hold `@` (start), `.` (open), `#` (wall), keys `a`–`f` and locks `A`–`F`. Each step moves
up, down, left or right. Stepping on a key picks it up; you can walk through a lock only while holding
its key. The keys are the first `k` letters, one of each, and a lock only appears if its key does.
Return the fewest steps to hold every key, or `None` if you can't.
