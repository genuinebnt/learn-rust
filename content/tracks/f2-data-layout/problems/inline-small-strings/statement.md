A columnar database stores millions of short strings (country codes, user names, status tags), each
a `String`: 24 bytes plus a heap allocation, even for `"DE"`.

Write `SmallStr`, an immutable string that keeps up to `INLINE_CAP` = **22** bytes inside the value
and puts longer ones on the heap:

- `size_of::<SmallStr>()` is **24**, the same as `String`, and so is `Option<SmallStr>`;
- `new` makes **no** allocation for strings of up to 22 bytes and **exactly one** for longer ones;
  cloning follows the same rule;
- `as_str`, `Deref<Target = str>`, `is_inline`, `Debug` and `Display` (both print like the `&str`);
- `Eq`, `Hash` and `Ord` agree with `str`'s, because `Borrow<str>` lets a `HashSet<SmallStr>` or
  `BTreeSet<SmallStr>` be searched with a plain `&str`.
