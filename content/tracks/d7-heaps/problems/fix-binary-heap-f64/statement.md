`top_k` keeps the highest readings in a `BinaryHeap<Reverse<Reading>>`, and other code keeps `Reading`s
in `BTreeSet`s and `HashSet`s. None of it compiles.

Make `Reading` a lawful key, ordered by the IEEE 754 total order (`f64::total_cmp`):

- `-0.0` ranks below `0.0`, and the two are **not** equal;
- a NaN equals itself (`Eq` is reflexive). A positive NaN ranks above `+∞`, a negative one below `-∞`;
- `==`, `<`, `cmp`, `partial_cmp` and hashing all agree with each other.

Fix `Reading`; leave `top_k` as it is.
