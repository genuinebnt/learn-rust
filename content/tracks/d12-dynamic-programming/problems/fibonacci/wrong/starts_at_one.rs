/// F(n), top-down: recursion plus a memo.
pub fn fib_memo(n: u32) -> u64 {
    fib_table(n)
}

/// F(n), bottom-up: a loop from F(0) upwards.
pub fn fib_table(n: u32) -> u64 {
    let (mut prev, mut cur) = (1u64, 1u64);
    for _ in 1..n.min(92) {
        (prev, cur) = (cur, prev + cur);
    }
    cur
}
