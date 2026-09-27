`F(0) = 0`, `F(1) = 1`, and `F(n) = F(n - 1) + F(n - 2)`.

Write it twice:
- `fib_memo`: recursion that remembers every `F(k)` it has already computed;
- `fib_table`: a loop that builds the answers from `F(0)` upwards.

`n` goes up to 93, the largest `F(n)` that fits in a `u64`. Plain recursion without a memo
takes far too long there.
