use solution::*;

#[test]
fn tick_example() {
    let mut p = Pool::new(vec![Conn { id: 1, idle: 0, tokens: 0 }, Conn { id: 2, idle: 8, tokens: 3 }, Conn { id: 3, idle: 2, tokens: 9 }], 10, 2, 10);
    let closed = p.tick(3);
    check!(r#"conns 1 (idle 0, 0 tokens), 2 (idle 8, 3), 3 (idle 2, 9); max_idle 10, refill 2, cap 10; tick 3"#, (closed, p.conns.iter().map(|c| (c.id, c.idle, c.tokens)).collect::<Vec<_>>(), p.drain_closed()), (1, vec![(1, 3, 2), (3, 5, 10)], vec![2]));
}

#[test]
fn use_conn() {
    let mut p = Pool::new(vec![Conn { id: 1, idle: 0, tokens: 0 }, Conn { id: 2, idle: 8, tokens: 3 }, Conn { id: 3, idle: 2, tokens: 9 }], 10, 2, 10);
    check!(r#"conns 1 (idle 0, 0 tokens), 2 (idle 8, 3), 3 (idle 2, 9); max_idle 10, refill 2, cap 10; use 2, use 1, use 9"#, (p.use_conn(2), p.use_conn(1), p.use_conn(9), p.conns.iter().map(|c| (c.id, c.idle, c.tokens)).collect::<Vec<_>>()), (true, false, false, vec![(1, 0, 0), (2, 0, 2), (3, 2, 9)]));
}

#[test]
fn idle_at_limit_stays() {
    let mut p = Pool::new(vec![Conn { id: 1, idle: 0, tokens: 0 }, Conn { id: 2, idle: 8, tokens: 3 }, Conn { id: 3, idle: 2, tokens: 9 }], 10, 2, 10);
    check!(r#"conns 1 (idle 0, 0 tokens), 2 (idle 8, 3), 3 (idle 2, 9); max_idle 10, refill 2, cap 10; tick 2"#, (p.tick(2), p.conns.iter().map(|c| (c.id, c.idle, c.tokens)).collect::<Vec<_>>()), (0, vec![(1, 2, 2), (2, 10, 5), (3, 4, 10)]));
}

#[test]
fn drain_starts_over() {
    let mut p = Pool::new(vec![Conn { id: 1, idle: 0, tokens: 0 }, Conn { id: 2, idle: 8, tokens: 3 }, Conn { id: 3, idle: 2, tokens: 9 }], 10, 2, 10);
    p.tick(100);
    check!(r#"conns 1 (idle 0, 0 tokens), 2 (idle 8, 3), 3 (idle 2, 9); max_idle 10, refill 2, cap 10; tick 100; drain twice"#, (p.drain_closed(), p.drain_closed(), p.conns.len()), (vec![1, 2, 3], vec![], 0));
}

#[test]
fn use_resets_idle() {
    let mut p = Pool::new(vec![Conn { id: 1, idle: 0, tokens: 0 }, Conn { id: 2, idle: 8, tokens: 3 }, Conn { id: 3, idle: 2, tokens: 9 }], 10, 2, 10);
    p.tick(1);
    p.use_conn(2);
    check!(r#"conns 1 (idle 0, 0 tokens), 2 (idle 8, 3), 3 (idle 2, 9); max_idle 10, refill 2, cap 10; tick 1; use 2; tick 2"#, (p.tick(2), p.conns.iter().map(|c| (c.id, c.idle, c.tokens)).collect::<Vec<_>>()), (0, vec![(1, 3, 4), (2, 2, 6), (3, 5, 10)]));
}

#[test]
fn stale_count_given() {
    let mut p = Pool::new(vec![Conn { id: 1, idle: 0, tokens: 0 }, Conn { id: 2, idle: 8, tokens: 3 }, Conn { id: 3, idle: 2, tokens: 9 }], 10, 2, 10);
    p.tick(3);
    check!(r#"stale_count reads what tick leaves"#, p.stale_count(), 0);
}
