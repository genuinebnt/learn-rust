use solution::*;

#[test]
fn empty_payload() {
    let (ev, n) = anneal_prelude::allocs(|| Event::packet(3, &[]));
    check!(r#"Event::packet(3, &[])"#, (ev.payload().map(|p| p.len()), ev.conn(), n.count), (Some(0), Some(3), 1));
}

#[test]
fn full_mtu_payload() {
    let data = vec![0xABu8; MTU];
    let (ev, n) = anneal_prelude::allocs(|| Event::packet(4, &data));
    check!(r#"Event::packet(4, 1500 bytes of 0xAB)"#, (ev.payload() == Some(&data[..]), n.count), (true, 1));
}

#[test]
#[should_panic]
fn over_mtu_panics() {
    Event::packet(1, &[0; MTU + 1]);
}

#[test]
fn clone_small_is_free() {
    let (t, a) = (Event::Tick(1), Event::Ack { conn: 1, seq: 2 });
    let (_, n) = anneal_prelude::allocs(|| (t.clone(), a.clone()));
    check!(r#"allocations to clone Tick(1) and Ack { 1, 2 }"#, n.count, 0);
}

#[test]
fn clone_packet_copies() {
    let ev = Event::packet(2, &[9, 9]);
    let (copy, n) = anneal_prelude::allocs(|| ev.clone());
    check!(r#"clone of packet(2, [9, 9]): equal, one allocation"#, (copy == ev, copy.payload(), n.count), (true, Some(&[9u8, 9][..]), 1));
}

#[test]
fn queue_of_a_million_events() {
    let (q, n) = anneal_prelude::allocs(|| std::collections::VecDeque::<Event>::with_capacity(1_000_000));
    drop(q);
    check!(r#"bytes requested by VecDeque::<Event>::with_capacity(1_000_000)"#, n.bytes, 16_000_000);
}

#[test]
fn equality() {
    check!(r#"packet(1, [1]) vs packet(1, [1]), packet(2, [1]), packet(1, [2])"#, (Event::packet(1, &[1]) == Event::packet(1, &[1]), Event::packet(1, &[1]) == Event::packet(2, &[1]), Event::packet(1, &[1]) == Event::packet(1, &[2])), (true, false, false));
}

#[test]
fn drain_empty() {
    check!(r#"drain of an empty queue"#, drain(&mut std::collections::VecDeque::new()), Summary::default());
}

#[test]
fn drain_bytes_add_up() {
    let mut q: std::collections::VecDeque<Event> = vec![Event::packet(1, &[0; 1000]), Event::packet(2, &[1; 1500]), Event::Close(2), Event::Close(1)].into();
    check!(r#"drain [packet(1, 1000 B), packet(2, 1500 B), Close(2), Close(1)]"#, drain(&mut q), Summary { last_tick: 0, acks: 0, packets: 2, bytes: 2500, closed: vec![2, 1] });
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(8204);
    for _ in 0..150 {
        let mut queue = std::collections::VecDeque::new();
        let (mut last_tick, mut acks, mut packets, mut bytes, mut closed) = (0, 0, 0, 0, Vec::new());
        let mut log = Vec::new();
        for _ in 0..rng.below(12) {
            let conn = rng.int(0, 9) as u32;
            let ev = match rng.below(4) {
                0 => {
                    last_tick = rng.int(0, 1_000_000) as u64;
                    log.push(format!("Tick({last_tick})"));
                    check!(format!("Tick({last_tick}).conn()"), Event::Tick(last_tick).conn(), None);
                    Event::Tick(last_tick)
                }
                1 => {
                    acks += 1;
                    log.push(format!("Ack {{ conn: {conn}, .. }}"));
                    Event::Ack { conn, seq: rng.int(0, 99) as u32 }
                }
                2 => {
                    closed.push(conn);
                    log.push(format!("Close({conn})"));
                    Event::Close(conn)
                }
                _ => {
                    let n = if rng.bool() { rng.below(20) } else { rng.below(MTU + 1) };
                    let data: Vec<u8> = rng.vec(n, 0, 255);
                    let ev = Event::packet(conn, &data);
                    log.push(format!("packet({conn}, {n} bytes)"));
                    check!(format!("packet({conn}, {n} bytes): conn, payload, clone == original"), (ev.conn(), ev.payload() == Some(&data[..]), ev.clone() == ev), (Some(conn), true, true));
                    packets += 1;
                    bytes += n;
                    ev
                }
            };
            queue.push_back(ev);
        }
        let want = Summary { last_tick, acks, packets, bytes, closed };
        check!(format!("drain [{}]", log.join(", ")), drain(&mut queue), want);
    }
}
