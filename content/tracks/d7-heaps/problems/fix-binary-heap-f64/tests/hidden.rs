use solution::*;

fn show(rs: &[Reading]) -> Vec<String> {
    rs.iter().map(|r| r.0.to_string()).collect()
}

#[test]
fn fewer_than_k() {
    check!(r#"readings = [2.0, 7.5], k = 5"#, show(&top_k(&[2.0, 7.5], 5)), vec!["7.5", "2"]);
}

#[test]
fn negatives() {
    check!(r#"readings = [-1.0, -2.0, 0.5], k = 2"#, show(&top_k(&[-1.0, -2.0, 0.5], 2)), vec!["0.5", "-1"]);
}

#[test]
fn only_negatives() {
    check!(r#"readings = [-3.0, -1.5, -2.0, -10.0], k = 3"#, show(&top_k(&[-3.0, -1.5, -2.0, -10.0], 3)), vec!["-1.5", "-2", "-3"]);
}

#[test]
fn infinities() {
    check!(r#"readings = [-inf, 5.0, inf, -0.0], k = 4"#, show(&top_k(&[f64::NEG_INFINITY, 5.0, f64::INFINITY, -0.0], 4)), vec!["inf", "5", "-0", "-inf"]);
}

#[test]
fn duplicates() {
    check!(r#"readings = [2.0, 1.0, 2.0], k = 2"#, show(&top_k(&[2.0, 1.0, 2.0], 2)), vec!["2", "2"]);
}

#[test]
fn only_nan() {
    check!(r#"readings = [NaN, NaN], k = 2"#, show(&top_k(&[f64::NAN, f64::NAN], 2)), Vec::<String>::new());
}

#[test]
fn empty() {
    check!(r#"readings = [], k = 3"#, show(&top_k(&[], 3)), Vec::<String>::new());
}

#[test]
fn nan_signs() {
    check!(r#"Reading(-NaN) < Reading(-inf), Reading(inf) < Reading(NaN), Reading(NaN) == Reading(-NaN)"#, (Reading(-f64::NAN) < Reading(f64::NEG_INFINITY), Reading(f64::INFINITY) < Reading(f64::NAN), Reading(f64::NAN) == Reading(-f64::NAN)), (true, true, false));
}

#[test]
fn btree_set() {
    let set: std::collections::BTreeSet<Reading> = [f64::NAN, f64::NAN, 0.0, -0.0, 1.0, f64::NEG_INFINITY].into_iter().map(Reading).collect();
    check!(r#"BTreeSet of NaN, NaN, 0.0, -0.0, 1.0, -inf"#, show(&set.into_iter().collect::<Vec<_>>()), vec!["-inf", "-0", "0", "1", "NaN"]);
}

#[test]
fn hash_set() {
    let set: std::collections::HashSet<Reading> = [f64::NAN, f64::NAN, 0.0, -0.0, 0.0, 2.5].into_iter().map(Reading).collect();
    check!(r#"HashSet of NaN, NaN, 0.0, -0.0, 0.0, 2.5"#, set.len(), 4);
}

#[test]
fn partial_cmp_is_total() {
    check!(r#"Reading(NaN).partial_cmp(&Reading(1.0)), Reading(0.0).partial_cmp(&Reading(-0.0))"#, (Reading(f64::NAN).partial_cmp(&Reading(1.0)), Reading(0.0).partial_cmp(&Reading(-0.0))), (Some(std::cmp::Ordering::Greater), Some(std::cmp::Ordering::Greater)));
}

#[test]
fn laws_hold_for_every_pair() {
    use std::cmp::Ordering;
    use std::hash::{DefaultHasher, Hash, Hasher};
    let hash = |r: &Reading| {
        let mut h = DefaultHasher::new();
        r.hash(&mut h);
        h.finish()
    };
    let pool = [f64::NAN, -f64::NAN, f64::NEG_INFINITY, -2.5, -0.0, 0.0, 1.0, 3.25, f64::INFINITY, f64::MIN_POSITIVE, f64::MAX];
    for &x in &pool {
        for &y in &pool {
            let (a, b) = (Reading(x), Reading(y));
            let order = x.total_cmp(&y);
            let got = (a.cmp(&b), a.partial_cmp(&b), a == b, a < b, a >= b);
            let want = (order, Some(order), order == Ordering::Equal, order == Ordering::Less, order != Ordering::Less);
            check!(format!("Reading({x:?}) vs Reading({y:?}): (cmp, partial_cmp, ==, <, >=)"), got, want);
            if a == b {
                check!(format!("hash(Reading({x:?})) == hash(Reading({y:?})) since they are equal"), hash(&a) == hash(&b), true);
            }
        }
    }
}

#[test]
fn random_vs_reference() {
    let mut rng = anneal_prelude::Rng::new(705);
    let pool = [f64::NAN, -f64::NAN, -2.5, -0.0, 0.0, 1.0, 3.25, 3.25, f64::INFINITY, f64::NEG_INFINITY];
    for _ in 0..300 {
        let n = rng.below(10);
        let readings: Vec<f64> = (0..n).map(|_| *rng.pick(&pool)).collect();
        let k = rng.below(6);
        let mut want: Vec<f64> = readings.iter().copied().filter(|x| !x.is_nan()).collect();
        want.sort_by(|a, b| b.total_cmp(a));
        want.truncate(k);
        let want: Vec<String> = want.iter().map(|x| x.to_string()).collect();
        check!(format!("readings = {readings:?}, k = {k}"), show(&top_k(&readings, k)), want);
    }
}

#[test]
fn scale_200k_readings() {
    let mut rng = anneal_prelude::Rng::new(706);
    let readings: Vec<f64> = (0..200_000).map(|i| if i % 1000 == 0 { f64::NAN } else { rng.int(-1_000_000, 1_000_000) as f64 / 4.0 }).collect();
    let mut want: Vec<f64> = readings.iter().copied().filter(|x| !x.is_nan()).collect();
    want.sort_by(|a, b| b.total_cmp(a));
    want.truncate(1000);
    let got: Vec<f64> = top_k(&readings, 1000).iter().map(|r| r.0).collect();
    check!("200000 random readings (every 1000th NaN), k = 1000", got == want, true);
}
