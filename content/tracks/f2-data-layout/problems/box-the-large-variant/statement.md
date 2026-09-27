A network thread feeds a connection thread through a `VecDeque<Event>`. Almost every event is a `Tick`,
an `Ack` or a `Close`, but `Event::Packet` carries its 1500-byte buffer inline, so every event is
1512 bytes and the queue moves 1.5 KB per tick (clippy's `large_enum_variant` warns about exactly this).

Make `Event` **16 bytes** (and `Option<Event>` too), keeping the public API: `Event::Tick(t)`,
`Event::Ack { conn, seq }` and `Event::Close(conn)` are still built directly, packets through
`Event::packet(conn, payload)`, and `conn`, `payload` and `drain` behave as before.

Allocation budget: building a packet event makes **exactly one** allocation; ticks, acks and closes
make none.
