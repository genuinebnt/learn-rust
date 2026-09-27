use solution::*;

#[test]
fn event_is_16_bytes() {
    check!(r#"size_of::<Event>(), size_of::<Option<Event>>()"#, (std::mem::size_of::<Event>(), std::mem::size_of::<Option<Event>>()), (16, 16));
}

#[test]
fn packet_allocates_once() {
    let (ev, n) = anneal_prelude::allocs(|| Event::packet(7, b"hello"));
    check!(r#"allocations for Event::packet(7, b"hello")"#, (n.count, ev.payload(), ev.conn()), (1, Some(&b"hello"[..]), Some(7)));
}

#[test]
fn small_events_dont_allocate() {
    let mut q = std::collections::VecDeque::with_capacity(8);
    let (_, n) = anneal_prelude::allocs(|| {
        q.push_back(Event::Tick(1));
        q.push_back(Event::Ack { conn: 2, seq: 3 });
        q.push_back(Event::Close(4));
    });
    check!(r#"allocations for Tick(1), Ack { 2, 3 }, Close(4), pushed into a queue with room"#, (n.count, q.len()), (0, 3));
}

#[test]
fn accessors() {
    check!(r#"conn() and payload() of Tick(9), Ack { conn: 2, seq: 5 }, Close(3)"#, (Event::Tick(9).conn(), Event::Ack { conn: 2, seq: 5 }.conn(), Event::Close(3).conn(), Event::Close(3).payload()), (None, Some(2), Some(3), None));
}

#[test]
fn drain_in_order() {
    let mut q: std::collections::VecDeque<Event> = vec![Event::Tick(5), Event::packet(1, &[1, 2, 3]), Event::Ack { conn: 1, seq: 9 }, Event::Close(1), Event::Tick(8)].into();
    check!(r#"drain [Tick(5), packet(1, [1, 2, 3]), Ack { 1, 9 }, Close(1), Tick(8)]"#, (drain(&mut q), q.is_empty()), (Summary { last_tick: 8, acks: 1, packets: 1, bytes: 3, closed: vec![1] }, true));
}
