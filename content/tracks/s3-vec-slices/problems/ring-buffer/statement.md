`Ring<T>` holds up to `capacity` items. `push` adds to the newest end and, when full, evicts
and returns the oldest. `iter` yields oldest to newest.
