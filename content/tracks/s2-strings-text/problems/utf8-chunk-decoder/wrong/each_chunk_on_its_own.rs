#[derive(Default)]
pub struct Utf8Decoder {}

impl Utf8Decoder {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn push(&mut self, chunk: &[u8], out: &mut String) {
        out.push_str(&String::from_utf8_lossy(chunk));
    }

    pub fn finish(self, _out: &mut String) {}
}
