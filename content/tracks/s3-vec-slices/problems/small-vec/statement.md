`SmallVec4<T>` keeps up to four items inline, with no heap allocation, and moves them into a
`Vec` when a fifth arrives. Implement `new`, `push`, `len`, `get` and `is_inline` without `unsafe`.
