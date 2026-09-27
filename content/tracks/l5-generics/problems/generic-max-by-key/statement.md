`max_by_key` returns the item with the largest key, the **first** one on a tie, calling `key` once per item.
It's shaped like `Iterator::max_by_key`, so the key has to be an owned value. Callers want to compare by a
field without cloning it: `max_by_key(&people, |p| p.name.as_str())`. Those calls don't compile.

Change the signature so `key` returns a reference **into** the item, including to unsized data like `str`
and `[i32]`. The body can stay as it is.
