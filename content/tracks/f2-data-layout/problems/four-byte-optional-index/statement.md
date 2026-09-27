A compiler's symbol table is a hash map that chains through indices instead of pointers:
`heads[bucket]` is the first entry of the bucket, and each `Entry` links to the next with
`next: Option<Idx>`. There are millions of entries, so every byte counts.

1. **Quiz.** Fill in `OPTION_SIZES`: `size_of` of `N1` to `N8`, from reasoning alone (`size_of`,
   `align_of`, `offset_of!` and `Layout` are off limits in your code).
2. **Give `Idx` a niche.** Today `Option<Idx>` is 8 bytes and `Entry` 16. Change `Idx`'s
   representation so `Option<Idx>` is **4 bytes** and `Entry` **12**, keeping `Idx::new` and
   `index` (indices `0` to `Idx::MAX`, and `new` panics above that).
3. **Finish `ChainMap`:** `insert` (returns the old value; a new key goes to the front of its
   chain), `get`, and `chain_of(key)`: the keys in `key`'s bucket, front first.
