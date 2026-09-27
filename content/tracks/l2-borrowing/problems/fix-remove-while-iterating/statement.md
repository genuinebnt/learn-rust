`merge_runs` doesn't compile: it removes from the `Vec` it's iterating and writes to the element before.
An index loop with `remove` would compile but skip elements and cost O(n²) on long logs. Fix it with one
pass over the `Vec`, without `remove` and without cloning any event.
