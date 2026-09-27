use std::collections::VecDeque;

/// The largest payload a packet event carries.
pub const MTU: usize = 1500;

/// What the network thread hands the connection thread: millions a second, through a queue.
/// 16 bytes: a one-byte tag, padding, and 8 bytes of payload (a `u64`, two `u32`s, or a thin `Box`).
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Event {
    Tick(u64),
    Ack { conn: u32, seq: u32 },
    Close(u32),
    Packet(u32, Box<[u8]>),
}

impl Event {
    /// A packet event for `conn` carrying `payload`. Panics if `payload` is longer than `MTU`.
    pub fn packet(conn: u32, payload: &[u8]) -> Event {
        assert!(payload.len() <= MTU, "payload of {} bytes is over the MTU", payload.len());
        Event::Packet(conn, payload.into())
    }

    /// The connection an event is about, if any.
    pub fn conn(&self) -> Option<u32> {
        match self {
            Event::Tick(_) => None,
            Event::Ack { conn, .. } => Some(*conn),
            Event::Close(conn) => Some(*conn),
            Event::Packet(conn, _) => Some(*conn),
        }
    }

    pub fn payload(&self) -> Option<&[u8]> {
        match self {
            Event::Packet(_, data) => Some(data),
            _ => None,
        }
    }
}

/// What the connection thread saw in one batch.
#[derive(Debug, Default, PartialEq, Eq)]
pub struct Summary {
    pub last_tick: u64,
    pub acks: usize,
    pub packets: usize,
    pub bytes: usize,
    pub closed: Vec<u32>,
}

/// Empties `queue`, oldest first.
pub fn drain(queue: &mut VecDeque<Event>) -> Summary {
    let mut s = Summary::default();
    while let Some(ev) = queue.pop_front() {
        match &ev {
            Event::Tick(t) => s.last_tick = *t,
            Event::Ack { .. } => s.acks += 1,
            Event::Close(conn) => s.closed.push(*conn),
            _ => {
                s.packets += 1;
                s.bytes += ev.payload().map_or(0, <[u8]>::len);
            }
        }
    }
    s
}
