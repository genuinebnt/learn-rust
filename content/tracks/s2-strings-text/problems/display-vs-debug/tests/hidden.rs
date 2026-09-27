use solution::*;

#[test]
fn width() {
    check!(r#"{:>12} then |"#, format!("{:>12}|", Money { cents: 1234, currency: "USD" }), "   12.34 USD|".to_string());
}

#[test]
fn left() {
    check!(r#"{:<10} then |"#, format!("{:<10}|", Money { cents: 7, currency: "GBP" }), "0.07 GBP  |".to_string());
}

#[test]
fn debug_unchanged() {
    check!(r#"{:?}"#, format!("{:?}", Money { cents: 1, currency: "USD" }), "Money { cents: 1, currency: \"USD\" }".to_string());
}

#[test]
fn min_value() {
    check!(r#"i64::MIN cents"#, format!("{}", Money { cents: i64::MIN, currency: "X" }), "-92233720368547758.08 X".to_string());
}

#[test]
fn max_value() {
    check!(r#"i64::MAX cents"#, format!("{}", Money { cents: i64::MAX, currency: "X" }), "92233720368547758.07 X".to_string());
}

#[test]
fn centered() {
    check!(r#"{:^12} then |"#, format!("{:^12}|", Money { cents: 1234, currency: "USD" }), " 12.34 USD  |".to_string());
}

#[test]
fn fill_char() {
    check!(r#"{:*<12}"#, format!("{:*<12}", Money { cents: 7, currency: "GBP" }), "0.07 GBP****".to_string());
}

#[test]
fn width_too_small() {
    check!(r#"{:>3}"#, format!("{:>3}", Money { cents: 1234, currency: "USD" }), "12.34 USD".to_string());
}

#[test]
fn negative_whole() {
    check!(r#"-100 cents"#, format!("{}", Money { cents: -100, currency: "USD" }), "-1.00 USD".to_string());
}

#[test]
fn negative_padded() {
    check!(r#"{:>11} with -12345 cents"#, format!("{:>11}", Money { cents: -12345, currency: "USD" }), "-123.45 USD".to_string());
}

#[test]
fn negative_width() {
    check!(r#"{:>12} with -5 cents"#, format!("{:>12}", Money { cents: -5, currency: "EUR" }), "   -0.05 EUR".to_string());
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2213);
    for _ in 0..300 {
        let cents = rng.int(-1_000_000_000_000, 1_000_000_000_000);
        let width = rng.below(24);
        let abs = cents.unsigned_abs();
        let mut plain = String::new();
        if cents < 0 {
            plain.push('-');
        }
        plain += &(abs / 100).to_string();
        plain.push('.');
        if abs % 100 < 10 {
            plain.push('0');
        }
        plain += &(abs % 100).to_string();
        plain += " JPY";
        let mut padded = " ".repeat(width.saturating_sub(plain.len()));
        padded += &plain;
        let m = Money { cents, currency: "JPY" };
        check!(format!("cents = {cents}, {{:>{width}}}"), (format!("{m}"), format!("{m:>width$}")), (plain, padded));
    }
}
