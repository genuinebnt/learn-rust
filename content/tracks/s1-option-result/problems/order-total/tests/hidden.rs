use solution::*;

#[test]
fn zero_qty() {
    check!(r#"lines = [("999", "0"), ("1", "1")]"#, order_total(&[("999", "0"), ("1", "1")]), Some(1));
}

#[test]
fn product_exactly_max() {
    check!(r#"lines = [("4294967295", "4294967297")]"#, order_total(&[("4294967295", "4294967297")]), Some(u64::MAX));
}

#[test]
fn sum_exactly_max() {
    check!(r#"lines = [("18446744073709551614", "1"), ("1", "1")]"#, order_total(&[("18446744073709551614", "1"), ("1", "1")]), Some(u64::MAX));
}

#[test]
fn sum_overflow_is_none() {
    check!(r#"lines = [("18446744073709551615", "1"), ("1", "1")]"#, order_total(&[("18446744073709551615", "1"), ("1", "1")]), None);
}

#[test]
fn field_too_big() {
    check!(r#"lines = [("18446744073709551616", "1")]"#, order_total(&[("18446744073709551616", "1")]), None);
}

#[test]
fn negative_price() {
    check!(r#"lines = [("-1", "1")]"#, order_total(&[("-1", "1")]), None);
}

#[test]
fn empty_field() {
    check!(r#"lines = [("", "1")]"#, order_total(&[("", "1")]), None);
}

#[test]
fn plus_sign_parses() {
    check!(r#"lines = [("+5", "2")]"#, order_total(&[("+5", "2")]), Some(10));
}

#[test]
fn spaces_do_not_parse() {
    check!(r#"lines = [("5", " 2")]"#, order_total(&[("5", " 2")]), None);
}

#[test]
fn full_width_digits() {
    check!(r#"lines = [("５", "2")]"#, order_total(&[("５", "2")]), None);
}

#[test]
fn bad_line_first() {
    check!(r#"lines = [("x", "1"), ("5", "2")]"#, order_total(&[("x", "1"), ("5", "2")]), None);
}

fn brute(s: &str) -> Option<u128> {
    let digits = s.strip_prefix('+').unwrap_or(s);
    if digits.is_empty() || !digits.bytes().all(|b| b.is_ascii_digit()) {
        return None;
    }
    let n = digits.bytes().fold(0u128, |n, b| (n * 10 + u128::from(b - b'0')).min(1 << 70));
    (n <= u128::from(u64::MAX)).then_some(n)
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1311);
    let field = |rng: &mut anneal_prelude::Rng| match rng.below(6) {
        0 => {
            let len = rng.below(4);
            rng.string(len, "012+x")
        }
        1 => rng.int(0, i64::MAX).to_string(),
        2 => (u64::MAX - rng.below(3) as u64).to_string(),
        _ => rng.int(0, 1000).to_string(),
    };
    for _ in 0..400 {
        let n = rng.below(5);
        let mut owned: Vec<(String, String)> = Vec::new();
        for _ in 0..n {
            let p = field(&mut rng);
            let q = field(&mut rng);
            owned.push((p, q));
        }
        let lines: Vec<(&str, &str)> = owned.iter().map(|(p, q)| (p.as_str(), q.as_str())).collect();
        let mut want = Some(0u128);
        for (p, q) in &lines {
            want = match (want, brute(p), brute(q)) {
                (Some(t), Some(p), Some(q)) if p * q <= u128::from(u64::MAX) && t + p * q <= u128::from(u64::MAX) => Some(t + p * q),
                _ => None,
            };
        }
        check!(format!("lines = {lines:?}"), order_total(&lines), want.map(|t| t as u64));
    }
}

#[test]
fn scale_many_lines() {
    let owned: Vec<(String, String)> = (0..200_000u64).map(|i| (i.to_string(), "2".to_string())).collect();
    let lines: Vec<(&str, &str)> = owned.iter().map(|(p, q)| (p.as_str(), q.as_str())).collect();
    check!("200000 lines (i, 2) for i below 200000", order_total(&lines), Some(39_999_800_000u64));
}
