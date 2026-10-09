//! The layout of fields in a C-like struct, and the field order that wastes the least.

#[derive(Debug, PartialEq, Eq)]
pub struct Layout {
    pub offsets: Vec<usize>,
    pub size: usize,
    pub align: usize,
}

/// Rounds `n` up to a multiple of `align` (a power of two).
fn round_up(n: usize, align: usize) -> usize {
    n.div_ceil(align) * align
}

/// `fields[i] = (size, align)`.
pub fn layout(fields: &[(usize, usize)]) -> Layout {
    todo!("3b-c2: place each field at the next multiple of its alignment; round the total up")
}

/// The order of field indexes that gives the smallest total size.
pub fn packed_order(fields: &[(usize, usize)]) -> Vec<usize> {
    todo!("3b-c2: largest alignment first")
}
