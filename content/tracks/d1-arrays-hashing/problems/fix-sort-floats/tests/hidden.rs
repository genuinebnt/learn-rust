use solution::*;

#[test]
fn infinities() {
    check!(r#"[inf, -inf, 0.0]"#, { let mut v = vec![f64::INFINITY, f64::NEG_INFINITY, 0.0]; sort_readings(&mut v); v.iter().map(|x| x.to_string()).collect::<Vec<_>>() }, vec!["-inf", "0", "inf"]);
}

#[test]
fn empty() {
    check!(r#"[]"#, { let mut v: Vec<f64> = vec![]; sort_readings(&mut v); v.len() }, 0);
}

#[test]
fn single_nan() {
    check!(r#"[NaN]"#, { let mut v = vec![f64::NAN]; sort_readings(&mut v); v.iter().map(|x| x.to_string()).collect::<Vec<_>>() }, vec!["NaN"]);
}

#[test]
fn nans_at_front() {
    check!(r#"[NaN, NaN, 2.0, -3.5]"#, { let mut v = vec![f64::NAN, f64::NAN, 2.0, -3.5]; sort_readings(&mut v); v.iter().map(|x| x.to_string()).collect::<Vec<_>>() }, vec!["-3.5", "2", "NaN", "NaN"]);
}

#[test]
fn negative_zero_first() {
    check!(r#"[0.0, -0.0]"#, { let mut v = vec![0.0, -0.0]; sort_readings(&mut v); v.iter().map(|x| x.to_string()).collect::<Vec<_>>() }, vec!["-0", "0"]);
}

#[test]
fn duplicates() {
    check!(r#"[1.5, 1.5, -1.5]"#, { let mut v = vec![1.5, 1.5, -1.5]; sort_readings(&mut v); v.iter().map(|x| x.to_string()).collect::<Vec<_>>() }, vec!["-1.5", "1.5", "1.5"]);
}

#[test]
fn tiny_and_huge() {
    check!(r#"[f64::MAX, f64::MIN_POSITIVE, f64::MIN]"#, { let mut v = vec![f64::MAX, f64::MIN_POSITIVE, f64::MIN]; sort_readings(&mut v); v == vec![f64::MIN, f64::MIN_POSITIVE, f64::MAX] }, true);
}

#[test]
fn random_vs_reference() {
    let mut rng = anneal_prelude::Rng::new(24);
    let pool = [f64::NAN, -2.5, -0.0, 0.0, 1.0, 3.25, f64::INFINITY, f64::NEG_INFINITY];
    for _ in 0..300 {
        let n = rng.below(10);
        let v: Vec<f64> = (0..n).map(|_| *rng.pick(&pool)).collect();
        // Numbers ascending (-0 before 0), then every NaN.
        let mut want: Vec<f64> = v.iter().copied().filter(|x| !x.is_nan()).collect();
        want.sort_by(|a, b| (a, a.is_sign_positive()).partial_cmp(&(b, b.is_sign_positive())).unwrap());
        want.extend(v.iter().filter(|x| x.is_nan()));
        let mut got = v.clone();
        sort_readings(&mut got);
        let show = |xs: &[f64]| xs.iter().map(|x| x.to_string()).collect::<Vec<_>>();
        check!(format!("{:?}", show(&v)), show(&got), show(&want));
    }
}
