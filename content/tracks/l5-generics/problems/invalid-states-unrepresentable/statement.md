Build `NonEmpty<T>`, a list with at least one item, so that "empty" can't be expressed at all, and let the
API say so: `first`, `last` and `max` return `&T`, not `Option<&T>`.

- `pop` removes the last item but never the only one (it returns `None` instead).
- `max` returns the first of equal largest items; `sort` sorts ascending (equal items may be reordered).
- `NonEmpty::try_from(vec)` fails with `Empty` for an empty `Vec`; `into_vec` and `into_iter` give the
  items back in order; `map` keeps the length.
- There's no `Default`: a default `NonEmpty` would be empty.
