/// F(n), top-down: recursion plus a memo.
pub fn fib_memo(n: u32) -> u64 {
    fib_table(n)
}

/// F(n), bottom-up: a loop from F(0) upwards.
pub fn fib_table(n: u32) -> u64 {
    let (mut a, mut b) = (0u64, 1u64);
    for _ in 0..n {
        (a, b) = (b, a + b);
    }
    a
}
