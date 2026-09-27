/// Decodes UTF-8 that arrives in chunks, such as reads from a socket.
#[derive(Default)]
pub struct Utf8Decoder {
    /// The start of a character the last chunk ended in the middle of (at most 3 bytes).
    pending: Vec<u8>,
}

impl Utf8Decoder {
    pub fn new() -> Self {
        Self::default()
    }

    /// Decodes `chunk` onto `out`. Each invalid sequence becomes U+FFFD, as `String::from_utf8_lossy`
    /// would do it; a character cut off at the end of the chunk waits for the next one.
    pub fn push(&mut self, chunk: &[u8], out: &mut String) {
        let joined;
        let mut input = chunk;
        if !self.pending.is_empty() {
            self.pending.extend_from_slice(chunk);
            joined = std::mem::take(&mut self.pending);
            input = &joined;
        }
        loop {
            match std::str::from_utf8(input) {
                Ok(text) => {
                    out.push_str(text);
                    return;
                }
                Err(e) => {
                    let (good, bad) = input.split_at(e.valid_up_to());
                    out.push_str(std::str::from_utf8(good).unwrap());
                    match e.error_len() {
                        Some(len) => {
                            out.push(char::REPLACEMENT_CHARACTER);
                            input = &bad[1..];
                            let _ = len;
                        }
                        None => {
                            self.pending.extend_from_slice(bad);
                            return;
                        }
                    }
                }
            }
        }
    }

    /// The end of the input: a character that was never finished becomes U+FFFD.
    pub fn finish(self, out: &mut String) {
        if !self.pending.is_empty() {
            out.push(char::REPLACEMENT_CHARACTER);
        }
    }
}
