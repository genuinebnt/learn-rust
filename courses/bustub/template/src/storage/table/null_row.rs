//! A row of nullable cells with a null bitmap in front.

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Cell {
    Int(i64),
    Text(String),
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Ty {
    Int,
    Text,
}

pub fn encode_row(row: &[Option<Cell>]) -> Vec<u8> {
    todo!("3b-c1: the bitmap, then each non-NULL value")
}

pub fn decode_row(bytes: &[u8], types: &[Ty]) -> Option<Vec<Option<Cell>>> {
    todo!("3b-c1: read the bitmap, then the value of each column that is not NULL; refuse anything inconsistent")
}
