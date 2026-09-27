use solution::*;

#[test]
fn plain() {
    check!(r#"[2.5, -1.0, 1.0]"#, { let mut v = vec![2.5, -1.0, 1.0]; sort_readings(&mut v); v.iter().map(|x| x.to_string()).collect::<Vec<_>>() }, vec!["-1", "1", "2.5"]);
}

#[test]
fn nan_goes_last() {
    check!(r#"[3.0, NaN, 1.0]"#, { let mut v = vec![3.0, f64::NAN, 1.0]; sort_readings(&mut v); v.iter().map(|x| x.to_string()).collect::<Vec<_>>() }, vec!["1", "3", "NaN"]);
}

#[test]
fn negatives() {
    check!(r#"[-0.5, -2.0, 4.0]"#, { let mut v = vec![-0.5, -2.0, 4.0]; sort_readings(&mut v); v.iter().map(|x| x.to_string()).collect::<Vec<_>>() }, vec!["-2", "-0.5", "4"]);
}

#[test]
fn infinities() {
    check!(r#"[inf, -inf, 0.0]"#, { let mut v = vec![f64::INFINITY, f64::NEG_INFINITY, 0.0]; sort_readings(&mut v); v.iter().map(|x| x.to_string()).collect::<Vec<_>>() }, vec!["-inf", "0", "inf"]);
}

#[test]
fn several_nans() {
    check!(r#"[NaN, 2.0, NaN]"#, { let mut v = vec![f64::NAN, 2.0, f64::NAN]; sort_readings(&mut v); v.iter().map(|x| x.to_string()).collect::<Vec<_>>() }, vec!["2", "NaN", "NaN"]);
}
