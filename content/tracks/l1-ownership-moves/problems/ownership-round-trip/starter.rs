/// Messages waiting to be sent, up to a byte limit.
pub struct Outbox {
    msgs: Vec<String>,
    limit: usize,
    used: usize,
}

impl Outbox {
    /// An empty outbox with no limit.
    pub fn new() -> Self {
        todo!()
    }

    /// Builder: the same outbox, limited to `bytes` bytes of messages in total.
    pub fn limit(self, bytes: usize) -> Self {
        todo!()
    }

    /// Bytes still free.
    pub fn remaining(&self) -> usize {
        todo!()
    }

    /// Queues `msg` if it fits in the bytes left. If it doesn't, the caller gets the same `String` back.
    pub fn push(&mut self, msg: String) -> Result<(), String> {
        todo!()
    }

    /// Queues `raw` as a UTF-8 message. If it isn't valid UTF-8, or doesn't fit, the caller gets the same
    /// bytes back.
    pub fn push_bytes(&mut self, raw: Vec<u8>) -> Result<(), Vec<u8>> {
        todo!()
    }

    /// Consumes the outbox and hands over its messages, oldest first.
    pub fn into_messages(self) -> Vec<String> {
        todo!()
    }
}
