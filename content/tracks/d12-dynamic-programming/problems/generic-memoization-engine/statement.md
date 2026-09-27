Build `Memo<'a, K, V>`, a cache that turns a recursive function into a memoised one. The
function receives the memo itself, so it can ask for smaller keys:

```rust
let mut fib = Memo::<u64, u128>::new(|m, n| if n < 2 { n as u128 } else { m.get(n - 1) + m.get(n - 2) });
fib.get(90) // 2880067194370816120, computing each n once
```

- `new(f)` makes an empty memo for `f`. `f` may borrow local data (lifetime `'a`).
- `get(key)` returns `f(key)`, calling `f` for a key at most once, ever.
- `len()` is the number of keys cached so far; `is_empty()` whether that is zero.
