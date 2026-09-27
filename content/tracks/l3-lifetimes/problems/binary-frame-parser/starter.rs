#[derive(Debug, PartialEq)]
pub struct Frame<'a> {
    pub kind: u8,
    pub payload: &'a [u8],
}

pub const MAGIC: &[u8; 2] = b"AN";

pub fn parse_frame(buf: &[u8]) -> Option<(Frame<'_>, &[u8])> {
    todo!()
}

pub fn parse_all(buf: &[u8]) -> Option<Vec<Frame<'_>>> {
    todo!()
}
