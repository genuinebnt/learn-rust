`Store::get` returns `Ok(None)` for a missing key and `Err(Corrupt(key))` for a value that isn't an integer.
Write `require`, which reports a missing key as `Err(Missing(key))`, and `sum_or_zero`, which adds up
`keys` and counts missing ones as 0. Both pass the first `Corrupt` error straight through.
Then write `first_corrupt`, which returns the error of the first corrupt key in `keys`, or `None`.
