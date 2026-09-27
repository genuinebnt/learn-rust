An analytics engine keeps a nullable float column as `Vec<Option<f64>>`. `f64` has no spare bit
pattern, so every row costs 16 bytes, half of it tag and padding, and scans read twice the memory.

Change the representation to Arrow's: a buffer of values plus a **validity bitmap** with one bit per
row. Keep the API and behaviour, and:

- `with_capacity(n)` followed by `n` pushes makes at most **2** allocations and requests at most
  **8n + n/8 + 64** bytes;
- `null_count` is O(1);
- a NaN is a value, not a null: `push(Some(f64::NAN))` then `get` gives `Some(NaN)`;
- `count_gt(t)` never counts a null, whatever `t` is.
