#[derive(Debug, PartialEq)]
pub struct Frame<'a> {
    pub kind: u8,
    pub payload: &'a [u8],
}

pub const MAGIC: &[u8; 2] = b"AN";

pub fn parse_frame(buf: &[u8]) -> Option<(Frame<'_>, &[u8])> {
    let rest = buf.strip_prefix(MAGIC)?;
    let (&kind, rest) = rest.split_first()?;
    let (len, rest) = rest.split_first_chunk::<2>()?;
    let len = usize::from(u16::from_be_bytes(*len));
    if rest.len() < len {
        return None;
    }
    let (payload, rest) = rest.split_at(len);
    Some((Frame { kind, payload }, rest))
}

pub fn parse_all(mut buf: &[u8]) -> Option<Vec<Frame<'_>>> {
    let mut frames = Vec::new();
    while !buf.is_empty() {
        let (frame, rest) = parse_frame(buf)?;
        frames.push(frame);
        buf = rest;
    }
    Some(frames)
}
