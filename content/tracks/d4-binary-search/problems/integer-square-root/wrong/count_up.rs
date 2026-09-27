pub fn isqrt(x: u64) -> u64 {
    let mut r: u64 = 0;
    while (r + 1).checked_mul(r + 1).is_some_and(|sq| sq <= x) {
        r += 1;
    }
    r
}
