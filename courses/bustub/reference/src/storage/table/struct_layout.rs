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
    // @begin 3b-c2
    let mut offsets = Vec::with_capacity(fields.len());
    let mut end = 0;
    let mut align = 1;
    for &(size, a) in fields {
        let at = round_up(end, a);
        offsets.push(at);
        end = at + size;
        align = align.max(a);
    }
    Layout { offsets, size: round_up(end, align), align }
    //~ todo!("3b-c2: place each field at the next multiple of its alignment; round the total up")
    // @end
}

/// The order of field indexes that gives the smallest total size.
pub fn packed_order(fields: &[(usize, usize)]) -> Vec<usize> {
    // @begin 3b-c2
    let mut idx: Vec<usize> = (0..fields.len()).collect();
    idx.sort_by(|&a, &b| fields[b].1.cmp(&fields[a].1).then(a.cmp(&b)));
    idx
    //~ todo!("3b-c2: largest alignment first")
    // @end
}
