`Vec2<T>` implements `+`, `-`, unary `-`, `v * k`, `+=`, `.sum()` and `a.dot(b)`, but none of it compiles. Add the
bounds each impl needs, and no more: the tests use a number type that is neither `Copy` nor `Clone`. The tests
also write the bound `V: Dot`, with no type argument.
