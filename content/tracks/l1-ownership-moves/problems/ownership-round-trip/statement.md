Write `Outbox`, a queue of messages with a byte limit. Values move in and out of it; nothing is ever
copied:

- `Outbox::new().limit(10)` is a builder: `limit` takes the outbox by value and returns it.
- `push(msg)` queues `msg` if its length in bytes fits in what's left. If it doesn't fit, the `Err` holds
  the caller's own `String`, so they can retry without having lost it.
- `push_bytes(raw)` does the same for raw bytes: invalid UTF-8 or a message that doesn't fit gives the
  caller's own `Vec<u8>` back. A valid one is queued as a `String` that reuses the same buffer.
- `into_messages` consumes the outbox and returns its messages, oldest first.
