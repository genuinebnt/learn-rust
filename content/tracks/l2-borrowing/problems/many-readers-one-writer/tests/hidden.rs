use solution::*;

#[test]
fn single_slot() {
    check!(r#"1 slot, 3 hits"#, { let mut c = Counter::new(1); for _ in 0..3 { c.hit(0); } (c.total(), c.busiest()) }, (3, Some(0)));
}

#[test]
fn tie_later_first() {
    check!(r#"4 slots, hits on 3, 1"#, { let mut c = Counter::new(4); c.hit(3); c.hit(1); c.busiest() }, Some(1));
}

#[test]
fn zero_hits_total() {
    check!(r#"5 slots, no hits"#, { let c = Counter::new(5); (c.total(), c.busiest()) }, (0, Some(0)));
}

#[test]
fn readers_alongside() {
    check!(r#"two &Counter at once"#, { let mut c = Counter::new(2); c.hit(1); let (r1, r2) = (&c, &c); (r1.total(), r2.total(), r1.busiest(), r2.busiest()) }, (1, 1, Some(1), Some(1)));
}

#[test]
fn many_hits() {
    check!(r#"1 slot, 100000 hits"#, { let mut c = Counter::new(1); for _ in 0..100_000 { c.hit(0); } c.total() }, 100_000);
}

#[test]
fn many_slots() {
    check!(r#"1000 slots, slot 999 hit twice"#, { let mut c = Counter::new(1000); c.hit(999); c.hit(999); c.hit(0); c.busiest() }, Some(999));
}

#[test]
fn overtakes() {
    check!(r#"hits on 0, 1, 1"#, { let mut c = Counter::new(2); c.hit(0); c.hit(1); c.hit(1); c.busiest() }, Some(1));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2002);
    for _ in 0..300 {
        let slots = 1 + rng.below(8);
        let k = rng.below(30);
        let hits: Vec<usize> = (0..k).map(|_| rng.below(slots)).collect();
        let mut c = Counter::new(slots);
        let mut model = vec![0u32; slots];
        for &h in &hits {
            c.hit(h);
            model[h] += 1;
        }
        let max = *model.iter().max().unwrap();
        let want = (model.iter().sum::<u32>(), model.iter().position(|&m| m == max));
        check!(format!("{slots} slots, hits on {hits:?}"), (c.total(), c.busiest()), want);
    }
}
