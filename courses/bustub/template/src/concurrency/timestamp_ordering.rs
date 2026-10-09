//! One item under basic timestamp ordering.

#[derive(Debug, PartialEq, Eq)]
pub struct Abort;

pub struct ToItem {
    _item: (),
}

impl ToItem {
    pub fn new(initial: i64) -> ToItem {
        todo!("4a-c5: an item nobody has touched")
    }

    pub fn read(&mut self, ts: u64) -> Result<i64, Abort> {
        todo!("4a-c5: refuse a read that is older than the last write; otherwise note it")
    }

    pub fn write(&mut self, ts: u64, value: i64) -> Result<(), Abort> {
        todo!("4a-c5: refuse a write that is older than a later read or write; otherwise apply it")
    }

    pub fn timestamps(&self) -> (u64, u64) {
        todo!("4a-c5: (read timestamp, write timestamp)")
    }
}
