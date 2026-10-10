//! Mapping a hash onto a range without a division.

/// A value in `0..n` (0 when `n == 0`), non-decreasing in `h`.
pub fn reduce(h: u32, n: u32) -> u32 {
    // @begin 0c-c4
    ((h as u64 * n as u64) >> 32) as u32
    //~ todo!("0c-c4: multiply in 64 bits and keep the high half")
    // @end
}

/// The top `bits` bits of `h` (`bits` in `0..=32`).
pub fn reduce_pow2(h: u32, bits: u32) -> u32 {
    // @begin 0c-c4
    if bits == 0 {
        0
    } else {
        h >> (32 - bits)
    }
    //~ todo!("0c-c4: shift the low bits away")
    // @end
}
