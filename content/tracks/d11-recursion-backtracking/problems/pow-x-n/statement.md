Return `x` raised to the power `n`. `n` can be negative (then the answer is `1 / x^|n|`) and can be as large as
`i32::MAX` or as small as `i32::MIN`, so multiplying `x` in a loop `n` times is too slow.

`x⁰` is 1 for every `x`, including 0. Answers are compared with a relative tolerance of 10⁻⁹.
