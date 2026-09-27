use solution::*;

#[test]
fn contains_existing() {
    check!(r#"[5, 6) then [0, 100)"#, { let mut m = IntervalMap::new(); m.insert(5, 6, 1).unwrap(); m.insert(0, 100, 2) }, Err(2));
}

#[test]
fn inside_existing() {
    check!(r#"[0, 100) then [5, 6)"#, { let mut m = IntervalMap::new(); m.insert(0, 100, 1).unwrap(); m.insert(5, 6, 2) }, Err(2));
}

#[test]
fn fits_before() {
    check!(r#"[10, 20) then [0, 10)"#, { let mut m = IntervalMap::new(); m.insert(10, 20, 1).unwrap(); (m.insert(0, 10, 2), m.get(9).copied(), m.get(10).copied()) }, (Ok(()), Some(2), Some(1)));
}

#[test]
fn overlaps_start() {
    check!(r#"[10, 20) then [0, 11)"#, { let mut m = IntervalMap::new(); m.insert(10, 20, 1).unwrap(); m.insert(0, 11, 2) }, Err(2));
}

#[test]
fn reversed() {
    check!(r#"[5, 3)"#, IntervalMap::new().insert(5, 3, 'x'), Err('x'));
}

#[test]
fn max_bounds() {
    check!(r#"[0, u32::MAX)"#, { let mut m = IntervalMap::new(); m.insert(0, u32::MAX, 'x').unwrap(); (m.get(0).copied(), m.get(u32::MAX - 1).copied(), m.get(u32::MAX).copied()) }, (Some('x'), Some('x'), None));
}

#[test]
fn refused_changes_nothing() {
    check!(r#"[0, 10) → a; [5, 15) → b refused"#, { let mut m = IntervalMap::new(); m.insert(0, 10, "a").unwrap(); let r = m.insert(5, 15, "b"); (r, m.get(5).copied(), m.get(12).copied()) }, (Err("b"), Some("a"), None));
}

#[test]
fn gap() {
    check!(r#"[0, 10), [20, 30); get(15)"#, { let mut m = IntervalMap::new(); m.insert(0, 10, 1).unwrap(); m.insert(20, 30, 2).unwrap(); m.get(15).copied() }, None);
}

#[test]
fn same_start() {
    check!(r#"[0, 10) then [0, 5)"#, { let mut m = IntervalMap::new(); m.insert(0, 10, 1).unwrap(); m.insert(0, 5, 2) }, Err(2));
}

#[test]
fn fills_a_gap_exactly() {
    check!(r#"[0, 10), [20, 30), then [10, 20)"#, { let mut m = IntervalMap::new(); m.insert(0, 10, 1).unwrap(); m.insert(20, 30, 3).unwrap(); (m.insert(10, 20, 2), m.get(19).copied(), m.get(20).copied()) }, (Ok(()), Some(2), Some(3)));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4011);
    for _ in 0..300 {
        let mut m = IntervalMap::new();
        let mut model: Vec<(u32, u32, usize)> = Vec::new();
        let mut log = Vec::new();
        let n = rng.below(8);
        for id in 0..n {
            let (a, b) = (rng.below(20) as u32, rng.below(20) as u32);
            let ok = a < b && model.iter().all(|&(s, e, _)| e <= a || b <= s);
            if ok {
                model.push((a, b, id));
            }
            log.push(format!("[{a}, {b})"));
            check!(log.join(", "), m.insert(a, b, id), if ok { Ok(()) } else { Err(id) });
        }
        for p in 0..21u32 {
            let want = model.iter().find(|&&(s, e, _)| s <= p && p < e).map(|&(_, _, id)| id);
            check!(format!("{}; get({p})", log.join(", ")), m.get(p).copied(), want);
        }
    }
}

#[test]
fn scale_100k() {
    let mut m = IntervalMap::new();
    for i in (0..100_000u32).rev() {
        m.insert(i * 3, i * 3 + 2, i).unwrap();
    }
    let hits = (0..300_000u32).filter(|&p| m.get(p).is_some()).count();
    check!("100000 intervals [3i, 3i + 2); get every point below 300000", hits, 200_000);
}
