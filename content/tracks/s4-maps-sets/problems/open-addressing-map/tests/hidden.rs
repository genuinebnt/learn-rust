use solution::*;

#[test]
fn ten_thousand_keys_survive_resizes() {
    let mut m = OpenMap::new();
    for k in 0..10_000u64 {
        m.insert(k * 7919, k);
    }
    let all_found = (0..10_000u64).all(|k| m.get(k * 7919) == Some(&k));
    check!("insert 10000 keys", (m.len(), all_found), (10_000, true));
}

#[test]
fn remove_keeps_probe_chains_intact() {
    let mut m = OpenMap::new();
    for k in 0..100u64 {
        m.insert(k, k);
    }
    for k in (0..100u64).step_by(2) {
        m.remove(k);
    }
    let odd_found = (1..100u64).step_by(2).all(|k| m.get(k) == Some(&k));
    let even_gone = (0..100u64).step_by(2).all(|k| m.get(k).is_none());
    check!("insert 0..100, remove the even keys", (m.len(), odd_found, even_gone), (50, true, true));
}

#[test]
fn churn_reuses_tombstones() {
    let mut m = OpenMap::new();
    for round in 0..1000u64 {
        m.insert(round, round);
        m.remove(round);
    }
    m.insert(42, 1);
    check!("1000 insert/remove rounds", (m.len(), m.get(42).copied()), (1, Some(1)));
}
