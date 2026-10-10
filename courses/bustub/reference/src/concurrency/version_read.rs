//! Which version of a row does a reader see?

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Stamp {
    Commit(u64),
    Pending,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Version {
    pub writer: u64,
    pub stamp: Stamp,
    /// `None` is a delete.
    pub value: Option<i64>,
}

/// `chain` is newest first. Returns the value the reader sees (`None`: the row does not exist for it).
pub fn read_version(chain: &[Version], read_ts: u64, reader: u64) -> Option<i64> {
    // @begin 4a-c2
    for v in chain {
        let visible = match v.stamp {
            Stamp::Commit(ts) => ts <= read_ts,
            Stamp::Pending => v.writer == reader,
        };
        if visible {
            return v.value;
        }
    }
    None
    //~ todo!("4a-c2: the first version in the chain that this reader may see decides")
    // @end
}
