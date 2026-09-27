/// F(n), top-down: recursion plus a memo.
pub fn fib_memo(n: u32) -> u64 {
    fn go(k: usize, memo: &mut [Option<u64>]) -> u64 {
        if k < 2 {
            return k as u64;
        }
        if let Some(v) = memo[k] {
            return v;
        }
        go(k - 1, memo) + go(k - 2, memo)
    }
    let n = n as usize;
    go(n, &mut vec![None; n + 1])
}

/// F(n), bottom-up: a loop from F(0) upwards.
pub fn fib_table(n: u32) -> u64 {
    let (mut a, mut b) = (0u64, 1u64);
    for _ in 0..n {
        let next = a.wrapping_add(b);
        a = b;
        b = next;
    }
    a
}
