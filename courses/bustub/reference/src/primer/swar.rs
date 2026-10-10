//! Comparing the eight bytes of a u64 at once.

const LOW7: u64 = 0x7F7F_7F7F_7F7F_7F7F;
const HIGH: u64 = 0x8080_8080_8080_8080;

/// The high bit of each byte of `group` that equals `byte`, and no other bit.
pub fn match_byte(group: u64, byte: u8) -> u64 {
    // @begin 0c-c5
    // x has a zero byte exactly where `group` equals `byte`; detect zero bytes exactly (no false positives):
    let x = group ^ (u64::from(byte) * 0x0101_0101_0101_0101);
    !(((x & LOW7).wrapping_add(LOW7)) | x | LOW7) & HIGH
    //~ todo!("0c-c5: xor with the byte repeated eight times, then find the zero bytes of the result with arithmetic only")
    // @end
}

/// The index of the lowest flagged byte.
pub fn first_match(mask: u64) -> Option<usize> {
    // @begin 0c-c5
    if mask == 0 {
        None
    } else {
        Some(mask.trailing_zeros() as usize / 8)
    }
    //~ todo!("0c-c5: the position of the lowest set bit, divided by eight")
    // @end
}
