`MiniVec` works. Add `as_slice` and `as_mut_slice`, then `Deref` and `DerefMut` to `[T]`,
so `v.iter()`, `v.sort()` and `&v[1..]` all work on a `MiniVec`.
