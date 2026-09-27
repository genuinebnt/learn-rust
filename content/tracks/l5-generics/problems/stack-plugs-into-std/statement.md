`Stack<T>` works, but it doesn't fit in with std, so the tests don't compile. Make these work for **any** `T`
(the tests use a `Token` type with no derives):

- `Stack::default()`;
- `collect()` into a `Stack` and `extend` one (items are pushed in order, so the last one ends up on top);
- `for x in stack` and `for x in &stack`, both **top first**;
- `{}` printing as `[top, ..., bottom]` whenever `T: Display`.
