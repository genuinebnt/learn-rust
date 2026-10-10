//! Merging queued disk operations without changing what any read sees.

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Op {
    Write(u32, u8),
    Read(u32),
}

/// Drops every write that a later write to the same page makes pointless, unless a read of that page lies between the two.
pub fn coalesce(ops: &[Op]) -> Vec<Op> {
    // @begin 1b-c4
    let mut keep = vec![true; ops.len()];
    for (i, op) in ops.iter().enumerate() {
        let Op::Write(page, _) = *op else { continue };
        for later in &ops[i + 1..] {
            match *later {
                Op::Read(p) if p == page => break,
                Op::Write(p, _) if p == page => {
                    keep[i] = false;
                    break;
                }
                _ => {}
            }
        }
    }
    ops.iter().zip(keep).filter(|(_, k)| *k).map(|(o, _)| *o).collect()
    //~ todo!("1b-c4: keep every read; keep a write unless a later write to the same page follows with no read of the page between")
    // @end
}
