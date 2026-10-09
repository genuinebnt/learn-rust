//! Merging queued disk operations without changing what any read sees.

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Op {
    Write(u32, u8),
    Read(u32),
}

/// Drops every write that a later write to the same page makes pointless, unless a read of that page lies between the two.
pub fn coalesce(ops: &[Op]) -> Vec<Op> {
    todo!("1b-c4: keep every read; keep a write unless a later write to the same page follows with no read of the page between")
}
