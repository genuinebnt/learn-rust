pub fn kth_grammar(n: u32, k: u64) -> u8 {
    if n == 1 {
        return 0;
    }
    // Row n is row n - 1 followed by row n - 1 with every symbol flipped.
    let half = 1u64 << (n - 2);
    if k <= half { kth_grammar(n - 1, k) } else { 1 - kth_grammar(n - 1, k - half) }
}
