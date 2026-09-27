`Warehouse` doesn't compile: in several places it has shared access where it needs unique access. Each
one is written differently: a receiver, a map lookup, an iterator, a pattern on an `Option` field, a
closure. Fix them. `available` and `last` only read, and callers hold their results side by side, so
they must stay as they are.
