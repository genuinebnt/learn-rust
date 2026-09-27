Write `max_by_key`: the item whose `key` is largest, or `None` for an empty slice. On a tie, return the
**first** such item (`Iterator::max_by_key` returns the last one, so don't just call it).

Call `key` exactly once per item: it may be expensive. The keys can be any ordered type, including ones
that aren't `Copy` or `Clone`, like `String`. Add the bounds the body needs.
