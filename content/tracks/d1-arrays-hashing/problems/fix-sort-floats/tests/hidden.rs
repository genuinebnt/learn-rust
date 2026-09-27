use solution::*;

#[test]
fn infinities() {
    check!(r#"[inf, -inf, 0.0]"#, { let mut v = vec![f64::INFINITY, f64::NEG_INFINITY, 0.0]; sort_readings(&mut v); v.iter().map(|x| x.to_string()).collect::<Vec<_>>() }, vec!["-inf", "0", "inf"]);
}
