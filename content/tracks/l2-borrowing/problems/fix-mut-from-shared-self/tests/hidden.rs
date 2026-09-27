use solution::*;

#[test]
fn empty_warehouse() {
    let mut w = Warehouse::new();
    check!(r#"new warehouse"#, (w.count_low(1), w.ship_all(), w.log().len(), w.last()), (0, 0, 0, None));
}

#[test]
fn tag_without_last() {
    let mut w = Warehouse::new();
    w.tag_last("x");
    check!(r#"new warehouse; tag_last "x""#, w.last(), None);
}

#[test]
fn receive_adds_up() {
    let mut w = Warehouse::new();
    w.receive("a", 2);
    w.receive("a", 3);
    check!(r#"receive a 2, a 3"#, (w.available("a"), w.last()), (5, Some("a")));
}

#[test]
fn reserve_zero_touches() {
    let mut w = Warehouse::new();
    w.receive("bolt", 10);
    w.receive("nut", 4);
    check!(r#"receive bolt 10, nut 4; reserve bolt 0"#, (w.reserve("bolt", 0), w.last()), (0, Some("bolt")));
}

#[test]
fn reserve_when_all_reserved() {
    let mut w = Warehouse::new();
    w.receive("bolt", 10);
    w.receive("nut", 4);
    w.reserve("nut", 4);
    check!(r#"receive bolt 10, nut 4; reserve nut 4, then nut 1"#, (w.reserve("nut", 1), w.last(), w.available("nut")), (0, Some("nut"), 0));
}

#[test]
fn ship_twice() {
    let mut w = Warehouse::new();
    w.receive("bolt", 10);
    w.receive("nut", 4);
    w.reserve("bolt", 10);
    check!(r#"receive bolt 10, nut 4; reserve bolt 10; ship_all twice"#, (w.ship_all(), w.ship_all(), w.available("bolt"), w.log().len()), (1, 0, 0, 1));
}

#[test]
fn log_accumulates() {
    let mut w = Warehouse::new();
    w.receive("bolt", 10);
    w.receive("nut", 4);
    w.reserve("nut", 1);
    w.ship_all();
    w.reserve("bolt", 1);
    w.reserve("nut", 1);
    w.ship_all();
    check!(r#"receive bolt 10, nut 4; reserve nut 1; ship; reserve bolt 1, nut 1; ship"#, w.log().to_vec(), vec!["nut: 1", "bolt: 1", "nut: 1"]);
}

#[test]
fn count_low_counts_reserved() {
    let mut w = Warehouse::new();
    w.receive("bolt", 10);
    w.receive("nut", 4);
    w.reserve("bolt", 9);
    check!(r#"receive bolt 10, nut 4; reserve bolt 9; count_low(2), count_low(5), count_low(0)"#, (w.count_low(2), w.count_low(5), w.count_low(0)), (1, 2, 0));
}

#[test]
fn tag_then_receive() {
    let mut w = Warehouse::new();
    w.receive("bolt", 10);
    w.receive("nut", 4);
    w.tag_last("!");
    w.receive("bolt", 1);
    check!(r#"receive bolt 10, nut 4; tag_last "!"; receive bolt 1"#, (w.last(), w.available("bolt")), (Some("bolt"), 11));
}

#[test]
fn random_vs_model() {
    use std::collections::BTreeMap;
    let mut rng = anneal_prelude::Rng::new(6203);
    let names = ["a", "b", "c"];
    for _ in 0..300 {
        let mut w = Warehouse::new();
        let mut model: BTreeMap<&str, (u32, u32)> = BTreeMap::new();
        let mut last: Option<String> = None;
        let mut log: Vec<String> = Vec::new();
        let mut ops = Vec::new();
        for _ in 0..10 {
            let name = *rng.pick(&names);
            let q = rng.below(5) as u32;
            match rng.below(4) {
                0 => {
                    w.receive(name, q);
                    model.entry(name).or_default().0 += q;
                    last = Some(name.to_string());
                    ops.push(format!("receive {name} {q}"));
                }
                1 => {
                    let want = match model.get_mut(name) {
                        Some(s) => {
                            let n = q.min(s.0 - s.1);
                            s.1 += n;
                            last = Some(name.to_string());
                            n
                        }
                        None => 0,
                    };
                    ops.push(format!("reserve {name} {q}"));
                    check!(ops.join(", "), w.reserve(name, q), want);
                }
                2 => {
                    let mut n = 0;
                    for (k, s) in model.iter_mut() {
                        if s.1 > 0 {
                            log.push(format!("{k}: {}", s.1));
                            s.0 -= s.1;
                            s.1 = 0;
                            n += 1;
                        }
                    }
                    ops.push("ship_all".to_string());
                    check!(ops.join(", "), w.ship_all(), n);
                }
                _ => {
                    let want = model.values().filter(|s| s.0 - s.1 < q).count();
                    ops.push(format!("count_low {q}"));
                    check!(ops.join(", "), w.count_low(q), want);
                }
            }
        }
        check!(format!("{}; last, log", ops.join(", ")), (w.last(), w.log().to_vec()), (last.as_deref(), log.clone()));
        for n in names {
            let want = model.get(n).map_or(0, |s| s.0 - s.1);
            check!(format!("{}; available({n})", ops.join(", ")), w.available(n), want);
        }
    }
}
