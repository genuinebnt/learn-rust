pub fn kth_grammar(n: u32, k: u64) -> u8 {
    if n == 1 {
        return 0;
    }
    let half = 1u64 << (n - 2);
    if k <= half { kth_grammar(n - 1, k) } else { kth_grammar(n - 1, k - half) }
}
