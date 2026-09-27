use solution::*;

#[test]
fn out_of_order() {
    let mut m = TimeMap::new();
    m.set("k", "five", 5);
    m.set("k", "two", 2);
    check!(r#"set @5 then @2; get @3"#, m.get("k", 3), Some("two"));
}

#[test]
fn unknown_key() {
    check!(r#"get a key never set"#, TimeMap::new().get("nope", 1).is_none(), true);
}

#[test]
fn overwrite() {
    let mut m = TimeMap::new();
    m.set("k", "old", 1);
    m.set("k", "new", 1);
    check!(r#"set @1 twice"#, m.get("k", 1), Some("new"));
}

#[test]
fn time_bounds() {
    let mut m = TimeMap::new();
    m.set("k", "zero", 0);
    m.set("k", "max", u64::MAX);
    check!(r#"set k=zero@0 and k=max@u64::MAX; get @0, @u64::MAX - 1, @u64::MAX"#, (m.get("k", 0), m.get("k", u64::MAX - 1), m.get("k", u64::MAX)), (Some("zero"), Some("zero"), Some("max")));
}

#[test]
fn unicode() {
    let mut m = TimeMap::new();
    m.set("键", "värde", 2);
    check!(r#"set 键=värde@2; get @3"#, m.get("键", 3), Some("värde"));
}

#[test]
fn empty_key_and_value() {
    let mut m = TimeMap::new();
    m.set("", "", 1);
    check!(r#"set ""=""@1; get @1"#, m.get("", 1), Some(""));
}

#[test]
fn random_vs_brute_force() {
    let keys = ["a", "b", "c"];
    let vals = ["x", "y", "z", "w"];
    let mut rng = anneal_prelude::Rng::new(410);
    for _ in 0..100 {
        let mut m = TimeMap::new();
        let mut log: Vec<(&str, &str, u64)> = Vec::new();
        for _ in 0..20 {
            if rng.bool() {
                let (k, v, t) = (*rng.pick(&keys), *rng.pick(&vals), rng.int(0, 10) as u64);
                m.set(k, v, t);
                log.push((k, v, t));
            } else {
                let (k, t) = (*rng.pick(&keys), rng.int(0, 11) as u64);
                // Brute force: the last write to k with the largest time <= t.
                let best = log.iter().filter(|e| e.0 == k && e.2 <= t).map(|e| e.2).max();
                let want = best.and_then(|b| log.iter().rev().find(|e| e.0 == k && e.2 == b).map(|e| e.1));
                check!(format!("after set calls {log:?}: get({k:?}, {t})"), m.get(k, t), want);
            }
        }
    }
}

#[test]
fn scale_100k_sets_and_gets() {
    let mut m = TimeMap::new();
    for t in 0..100_000u64 {
        m.set("k", if t % 2 == 0 { "even" } else { "odd" }, 2 * t);
    }
    let odd = (0..200_000u64).filter(|&t| m.get("k", t) == Some("odd")).count();
    check!("100000 sets at times 0, 2, 4, …; 200000 gets", odd, 100_000);
}
