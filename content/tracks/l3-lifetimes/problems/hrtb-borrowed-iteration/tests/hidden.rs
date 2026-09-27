use solution::*;

#[test]
fn array() {
    check!(r#"[4, 4, 4]"#, Stats::new([4u32, 4, 4]).spread(), Some(0));
}

#[test]
fn single() {
    let s = Stats::new(vec![7u32]);
    check!(r#"[7]"#, (s.mean(), s.spread(), s.count_above(6)), (Some(7.0), Some(0), 1));
}

#[test]
fn sum_past_u32() {
    check!(r#"[u32::MAX, u32::MAX]"#, Stats::new(vec![u32::MAX, u32::MAX]).mean(), Some(u32::MAX as f64));
}

#[test]
fn full_spread() {
    check!(r#"[0, u32::MAX]"#, Stats::new([0u32, u32::MAX]).spread(), Some(u32::MAX));
}

#[test]
fn btreeset_dedups() {
    check!(r#"BTreeSet from [3, 3, 9]"#, Stats::new(std::collections::BTreeSet::from([3u32, 3, 9])).mean(), Some(6.0));
}

#[test]
fn linked_list() {
    let s = Stats::new(std::collections::LinkedList::from([2u32, 8, 5]));
    check!(r#"LinkedList [2, 8, 5]"#, (s.spread(), s.count_above(4)), (Some(6), 2));
}

#[test]
fn above_max() {
    check!(r#"[1, 2], above u32::MAX"#, Stats::new(vec![1u32, 2]).count_above(u32::MAX), 0);
}

#[test]
fn unsorted_spread() {
    check!(r#"[5, 1, 9, 3]"#, Stats::new(vec![5u32, 1, 9, 3]).spread(), Some(8));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(317);
    for _ in 0..300 {
        let n = rng.below(10);
        let v: Vec<u32> = rng.vec(n, 0, 20);
        let t = rng.int(0, 20) as u32;
        let mean = if n == 0 { None } else { Some(v.iter().map(|&x| x as f64).sum::<f64>() / n as f64) };
        let spread = if n == 0 { None } else { Some(v.iter().max().unwrap() - v.iter().min().unwrap()) };
        let above = v.iter().filter(|&&x| x > t).count();
        let s = Stats::new(v.clone());
        check!(format!("data = {v:?}, threshold = {t}"), (s.mean(), s.spread(), s.count_above(t)), (mean, spread, above));
    }
}

#[test]
fn scale_1m() {
    let s = Stats::new((0..1_000_000u32).collect::<Vec<_>>());
    check!("0..1000000", (s.mean(), s.spread(), s.count_above(999_990)), (Some(499_999.5), Some(999_999), 9));
}

#[test]
fn btreeset() {
    check!(r#"BTreeSet {1, 10}"#, Stats::new(std::collections::BTreeSet::from([1u32, 10])).mean(), Some(5.5));
}

#[test]
fn empty() {
    check!(r#"empty Vec"#, Stats::new(Vec::<u32>::new()).mean(), None);
}

#[test]
fn count() {
    check!(r#"[1, 5, 9], above 4"#, Stats::new(vec![1u32, 5, 9]).count_above(4), 2);
}

#[test]
fn reuse() {
    let s = Stats::new(vec![1u32, 2, 3]);
    check!(r#"call three methods on the same Stats"#, (s.mean(), s.spread(), s.count_above(0)), (Some(2.0), Some(2), 3));
}
