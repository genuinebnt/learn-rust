/// Decodes UTF-8 that arrives in chunks, such as reads from a socket.
#[derive(Default)]
pub struct Utf8Decoder {
    // Your state here.
}

impl Utf8Decoder {
    pub fn new() -> Self {
        Self::default()
    }

    /// Decodes `chunk` onto `out`. Each invalid sequence becomes U+FFFD, as `String::from_utf8_lossy`
    /// would do it; a character cut off at the end of the chunk waits for the next one.
    pub fn push(&mut self, chunk: &[u8], out: &mut String) {
        todo!()
    }

    /// The end of the input: a character that was never finished becomes U+FFFD.
    pub fn finish(self, out: &mut String) {
        todo!()
    }
}
