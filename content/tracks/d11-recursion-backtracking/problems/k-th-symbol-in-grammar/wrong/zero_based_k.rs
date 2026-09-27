pub fn kth_grammar(n: u32, k: u64) -> u8 {
    let _ = n;
    (k.count_ones() % 2) as u8
}
