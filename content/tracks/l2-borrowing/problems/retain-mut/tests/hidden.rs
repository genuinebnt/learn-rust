use solution::*;

#[test]
fn empty_pool() {
    let mut p = Pool::new(vec![], 1, 1, 1);
    check!(r#"no connections; tick 5"#, (p.tick(5), p.drain_closed()), (0, vec![]));
}

#[test]
fn tick_zero() {
    let mut p = Pool::new(vec![Conn { id: 1, idle: 0, tokens: 0 }, Conn { id: 2, idle: 8, tokens: 3 }, Conn { id: 3, idle: 2, tokens: 9 }], 10, 2, 10);
    check!(r#"conns 1 (idle 0, 0 tokens), 2 (idle 8, 3), 3 (idle 2, 9); max_idle 10, refill 2, cap 10; tick 0"#, (p.tick(0), p.conns.iter().map(|c| (c.id, c.idle, c.tokens)).collect::<Vec<_>>()), (0, vec![(1, 0, 2), (2, 8, 5), (3, 2, 10)]));
}

#[test]
fn closed_in_order_across_ticks() {
    let mut p = Pool::new(vec![Conn { id: 1, idle: 0, tokens: 0 }, Conn { id: 2, idle: 8, tokens: 3 }, Conn { id: 3, idle: 2, tokens: 9 }], 10, 2, 10);
    check!(r#"conns 1 (idle 0, 0 tokens), 2 (idle 8, 3), 3 (idle 2, 9); max_idle 10, refill 2, cap 10; tick 3, tick 6"#, { p.tick(3); p.tick(6); p.drain_closed() }, vec![2, 3]);
}

#[test]
fn refill_saturates() {
    let mut p = Pool::new(vec![Conn { id: 7, idle: 0, tokens: u32::MAX - 1 }], 10, 5, u32::MAX);
    check!(r#"tokens u32::MAX - 1, refill 5, cap u32::MAX"#, { p.tick(1); p.conns[0].tokens }, u32::MAX);
}

#[test]
fn cap_below_tokens() {
    let mut p = Pool::new(vec![Conn { id: 7, idle: 0, tokens: 9 }], 10, 0, 4);
    check!(r#"tokens 9, cap 4"#, { p.tick(1); p.conns[0].tokens }, 4);
}

#[test]
fn use_until_empty() {
    let mut p = Pool::new(vec![Conn { id: 5, idle: 4, tokens: 2 }], 10, 0, 9);
    check!(r#"tokens 2; use 3 times"#, (p.use_conn(5), p.use_conn(5), p.use_conn(5), p.conns[0].tokens), (true, true, false, 0));
}

#[test]
fn failed_use_keeps_idle() {
    let mut p = Pool::new(vec![Conn { id: 5, idle: 4, tokens: 0 }], 10, 0, 9);
    check!(r#"tokens 0, idle 4; use"#, (p.use_conn(5), p.conns[0].idle), (false, 4));
}

#[test]
fn duplicate_ids_first_used() {
    let mut p = Pool::new(vec![Conn { id: 5, idle: 0, tokens: 1 }, Conn { id: 5, idle: 0, tokens: 1 }], 10, 0, 9);
    check!(r#"two conns with id 5"#, (p.use_conn(5), p.conns[0].tokens, p.conns[1].tokens), (true, 0, 1));
}

#[test]
fn max_idle_zero() {
    let mut p = Pool::new(vec![Conn { id: 1, idle: 0, tokens: 0 }, Conn { id: 2, idle: 0, tokens: 0 }], 0, 1, 1);
    check!(r#"max_idle 0; tick 1 closes all"#, (p.tick(1), p.drain_closed()), (2, vec![1, 2]));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6219);
    for _ in 0..300 {
        let n = rng.below(6);
        let start: Vec<(u32, u64, u32)> = (0..n).map(|i| (i as u32, rng.below(6) as u64, rng.below(5) as u32)).collect();
        let (max_idle, refill, cap) = (rng.below(8) as u64, rng.below(3) as u32, rng.below(6) as u32);
        let mut p = Pool::new(start.iter().map(|&(id, idle, tokens)| Conn { id, idle, tokens }).collect(), max_idle, refill, cap);
        let mut model = start.clone();
        let mut closed = Vec::new();
        let mut ops = Vec::new();
        for _ in 0..5 {
            if rng.bool() {
                let dt = rng.below(4) as u64;
                let before = model.len();
                let mut kept = Vec::new();
                for (id, idle, tokens) in model {
                    if idle + dt > max_idle {
                        closed.push(id);
                    } else {
                        kept.push((id, idle + dt, (tokens + refill).min(cap)));
                    }
                }
                model = kept;
                ops.push(format!("tick {dt}"));
                check!(format!("{start:?}, max_idle {max_idle}, refill {refill}, cap {cap}; {}", ops.join(", ")), p.tick(dt), before - model.len());
            } else {
                let id = rng.below(n + 1) as u32;
                let want = match model.iter_mut().find(|c| c.0 == id) {
                    Some(c) if c.2 > 0 => {
                        c.2 -= 1;
                        c.1 = 0;
                        true
                    }
                    _ => false,
                };
                ops.push(format!("use {id}"));
                check!(format!("{start:?}, max_idle {max_idle}, refill {refill}, cap {cap}; {}", ops.join(", ")), p.use_conn(id), want);
            }
        }
        let got: Vec<(u32, u64, u32)> = p.conns.iter().map(|c| (c.id, c.idle, c.tokens)).collect();
        check!(format!("{start:?}, max_idle {max_idle}, refill {refill}, cap {cap}; {}; state", ops.join(", ")), (got, p.drain_closed()), (model, closed));
    }
}

#[test]
fn big_pool() {
    let conns: Vec<Conn> = (0..200_000).map(|i| Conn { id: i, idle: (i % 2) as u64 * 10, tokens: 0 }).collect();
    let mut p = Pool::new(conns, 5, 1, 3);
    let closed = p.tick(1);
    check!("200000 conns, every other one stale", (closed, p.conns.len(), p.conns[99_999].id, p.drain_closed()[99_999]), (100_000, 100_000, 199_998, 199_999));
}
