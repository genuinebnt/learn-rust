use solution::*;

fn evs(xs: &[(&str, u32)]) -> Vec<Event> {
    xs.iter().map(|&(k, c)| Event { key: k.to_string(), count: c }).collect()
}

fn pairs(v: &[Event]) -> Vec<(&str, u32)> {
    v.iter().map(|e| (e.key.as_str(), e.count)).collect()
}

#[test]
fn single() {
    let mut v = evs(&[("k", 9)]);
    let n = merge_runs(&mut v);
    check!(r#"events [("k", 9)]"#, (n, pairs(&v)), (0, vec![("k", 9)]));
}

#[test]
fn all_different() {
    let mut v = evs(&[("a", 1), ("b", 2), ("c", 3)]);
    let n = merge_runs(&mut v);
    check!(r#"events [("a", 1), ("b", 2), ("c", 3)]"#, (n, pairs(&v)), (0, vec![("a", 1), ("b", 2), ("c", 3)]));
}

#[test]
fn case_sensitive() {
    let mut v = evs(&[("a", 1), ("A", 1), ("a", 1)]);
    let n = merge_runs(&mut v);
    check!(r#"events [("a", 1), ("A", 1), ("a", 1)]"#, (n, pairs(&v)), (0, vec![("a", 1), ("A", 1), ("a", 1)]));
}

#[test]
fn zero_counts() {
    let mut v = evs(&[("z", 0), ("z", 0), ("y", 0)]);
    let n = merge_runs(&mut v);
    check!(r#"events [("z", 0), ("z", 0), ("y", 0)]"#, (n, pairs(&v)), (1, vec![("z", 0), ("y", 0)]));
}

#[test]
fn empty_keys() {
    let mut v = evs(&[("", 1), ("", 2), ("e", 3), ("", 4)]);
    let n = merge_runs(&mut v);
    check!(r#"events [("", 1), ("", 2), ("e", 3), ("", 4)]"#, (n, pairs(&v)), (1, vec![("", 3), ("e", 3), ("", 4)]));
}

#[test]
fn run_at_end() {
    let mut v = evs(&[("a", 1), ("b", 1), ("b", 2), ("b", 3)]);
    let n = merge_runs(&mut v);
    check!(r#"events [("a", 1), ("b", 1), ("b", 2), ("b", 3)]"#, (n, pairs(&v)), (2, vec![("a", 1), ("b", 6)]));
}

#[test]
fn unicode() {
    let mut v = evs(&[("日", 1), ("日", 1), ("é", 2)]);
    let n = merge_runs(&mut v);
    check!(r#"events [("日", 1), ("日", 1), ("é", 2)]"#, (n, pairs(&v)), (1, vec![("日", 2), ("é", 2)]));
}

#[test]
fn big_counts() {
    let mut v = evs(&[("m", 4_000_000_000), ("m", 294_967_295)]);
    merge_runs(&mut v);
    check!(r#"events [("m", 4000000000), ("m", 294967295)]"#, pairs(&v), vec![("m", u32::MAX)]);
}

#[test]
fn survivor_is_the_first() {
    let mut v = evs(&[("run", 1), ("run", 2)]);
    let p = v[0].key.as_ptr();
    merge_runs(&mut v);
    check!(r#"the merged event is the run's first String"#, p == v[0].key.as_ptr(), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6218);
    for _ in 0..300 {
        let n = rng.below(10);
        let mut xs: Vec<(String, u32)> = Vec::new();
        for _ in 0..n {
            xs.push((rng.string(1, "ab"), rng.below(5) as u32));
        }
        let mut want: Vec<(String, u32)> = Vec::new();
        for (k, c) in &xs {
            match want.last_mut() {
                Some((lk, lc)) if lk == k => *lc += c,
                _ => want.push((k.clone(), *c)),
            }
        }
        let mut v: Vec<Event> = xs.iter().map(|(k, c)| Event { key: k.clone(), count: *c }).collect();
        let removed = merge_runs(&mut v);
        let got: Vec<(String, u32)> = v.into_iter().map(|e| (e.key, e.count)).collect();
        check!(format!("events {xs:?}"), (removed, got), (n - want.len(), want));
    }
}

#[test]
fn long_log() {
    let mut v: Vec<Event> = (0..200_000).map(|i| Event { key: format!("k{}", i / 2), count: 1 }).collect();
    let removed = merge_runs(&mut v);
    check!("200000 events in runs of 2", (removed, v.len(), v[99_999].count), (100_000, 100_000, 2));
}
