use solution::*;

fn sessions(xs: &[(u32, Option<u32>, u64, u64)]) -> std::collections::HashMap<u32, Session> {
    xs.iter().map(|&(id, parent, expires, bytes)| (id, Session { parent, expires, bytes })).collect()
}

fn bytes(m: &std::collections::HashMap<u32, Session>) -> Vec<(u32, u64)> {
    let mut v: Vec<(u32, u64)> = m.iter().map(|(&id, s)| (id, s.bytes)).collect();
    v.sort();
    v
}

#[test]
fn empty() {
    let mut m = sessions(&[]);
    let removed = expire(&mut m, 3);
    check!(r#"sessions (id, parent, expires, bytes) ; now 3"#, (removed, bytes(&m)), (Vec::<u32>::new(), Vec::<(u32, u64)>::new()));
}

#[test]
fn all_expire() {
    let mut m = sessions(&[(1, None, 0, 1), (2, Some(1), 0, 2), (3, Some(2), 0, 3)]);
    let removed = expire(&mut m, 0);
    check!(r#"sessions (id, parent, expires, bytes) (1, None, 0, 1), (2, 1, 0, 2), (3, 2, 0, 3); now 0"#, (removed, bytes(&m)), (vec![1, 2, 3], Vec::<(u32, u64)>::new()));
}

#[test]
fn missing_parent() {
    let mut m = sessions(&[(1, Some(9), 0, 4), (2, None, 5, 1)]);
    let removed = expire(&mut m, 1);
    check!(r#"sessions (id, parent, expires, bytes) (1, 9, 0, 4), (2, None, 5, 1); now 1"#, (removed, bytes(&m)), (vec![1], vec![(2, 1)]));
}

#[test]
fn self_parent() {
    let mut m = sessions(&[(1, Some(1), 0, 4), (2, Some(2), 9, 1)]);
    let removed = expire(&mut m, 1);
    check!(r#"sessions (id, parent, expires, bytes) (1, 1, 0, 4), (2, 2, 9, 1); now 1"#, (removed, bytes(&m)), (vec![1], vec![(2, 1)]));
}

#[test]
fn siblings_add_up() {
    let mut m = sessions(&[(1, None, 9, 0), (2, Some(1), 1, 3), (3, Some(1), 1, 4), (4, Some(1), 1, 5)]);
    let removed = expire(&mut m, 2);
    check!(r#"sessions (id, parent, expires, bytes) (1, None, 9, 0), (2, 1, 1, 3), (3, 1, 1, 4), (4, 1, 1, 5); now 2"#, (removed, bytes(&m)), (vec![2, 3, 4], vec![(1, 12)]));
}

#[test]
fn grandchild_to_live_parent() {
    let mut m = sessions(&[(1, None, 9, 0), (2, Some(1), 9, 0), (3, Some(2), 1, 6)]);
    let removed = expire(&mut m, 2);
    check!(r#"sessions (id, parent, expires, bytes) (1, None, 9, 0), (2, 1, 9, 0), (3, 2, 1, 6); now 2"#, (removed, bytes(&m)), (vec![3], vec![(1, 0), (2, 6)]));
}

#[test]
fn big_bytes() {
    let mut m = sessions(&[(1, None, 9, 1099511627776), (2, Some(1), 1, 1099511627776)]);
    let removed = expire(&mut m, 1);
    check!(r#"sessions (id, parent, expires, bytes) (1, None, 9, 1099511627776), (2, 1, 1, 1099511627776); now 1"#, (removed, bytes(&m)), (vec![2], vec![(1, 2199023255552)]));
}

#[test]
fn unsorted_ids() {
    let mut m = sessions(&[(30, None, 1, 1), (10, None, 1, 1), (20, None, 9, 1)]);
    let removed = expire(&mut m, 5);
    check!(r#"sessions (id, parent, expires, bytes) (30, None, 1, 1), (10, None, 1, 1), (20, None, 9, 1); now 5"#, (removed, bytes(&m)), (vec![10, 30], vec![(20, 1)]));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6223);
    for _ in 0..300 {
        let n = rng.below(8) as u32;
        let xs: Vec<(u32, Option<u32>, u64, u64)> = (0..n).map(|id| (id, if rng.bool() { Some(rng.below(n as usize + 1) as u32) } else { None }, rng.below(6) as u64, rng.below(10) as u64)).collect();
        let now = rng.below(6) as u64;
        let mut want_removed: Vec<u32> = xs.iter().filter(|x| x.2 <= now).map(|x| x.0).collect();
        want_removed.sort();
        let mut left: Vec<(u32, u64)> = xs.iter().filter(|x| x.2 > now).map(|x| (x.0, x.3)).collect();
        for g in xs.iter().filter(|x| x.2 <= now) {
            if let Some(p) = g.1 {
                if let Some(e) = left.iter_mut().find(|e| e.0 == p) {
                    e.1 += g.3;
                }
            }
        }
        left.sort();
        let mut m = sessions(&xs);
        let removed = expire(&mut m, now);
        check!(format!("sessions {xs:?}; now {now}"), (removed, bytes(&m)), (want_removed, left));
    }
}

#[test]
fn many_sessions() {
    let xs: Vec<(u32, Option<u32>, u64, u64)> = (0..200_000u32).map(|id| (id, if id % 2 == 1 { Some(id - 1) } else { None }, if id % 2 == 1 { 5 } else { 100 }, 1)).collect();
    let mut m = sessions(&xs);
    let removed = expire(&mut m, 10);
    let b = bytes(&m);
    check!("200000 sessions, odd ones expire into their even parent", (removed.len(), b.len(), b[99_999]), (100_000, 100_000, (199_998, 2)));
}
