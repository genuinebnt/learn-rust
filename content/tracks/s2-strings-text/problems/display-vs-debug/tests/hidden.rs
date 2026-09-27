use solution::*;

#[test]
fn zero() {
    check!(r#"0 cents"#, format!("{}", Money { cents: 0, currency: "X" }), "0.00 X".to_string());
}

#[test]
fn whole_amount() {
    check!(r#"500 cents"#, format!("{}", Money { cents: 500, currency: "USD" }), "5.00 USD".to_string());
}

#[test]
fn left() {
    check!(r#"{:<10} then |"#, format!("{:<10}|", Money { cents: 7, currency: "GBP" }), "0.07 GBP  |".to_string());
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
fn min_value() {
    check!(r#"i64::MIN cents"#, format!("{}", Money { cents: i64::MIN, currency: "X" }), "-92233720368547758.08 X".to_string());
}

#[test]
fn max_value_plus() {
    check!(r#"{:+} with i64::MAX cents"#, format!("{:+}", Money { cents: i64::MAX, currency: "X" }), "+92233720368547758.07 X".to_string());
}

#[test]
fn negative_width() {
    check!(r#"{:>12} with -5 cents"#, format!("{:>12}", Money { cents: -5, currency: "EUR" }), "   -0.05 EUR".to_string());
}

#[test]
fn plus_zero() {
    check!(r#"{:+} with 0 cents"#, format!("{:+}", Money { cents: 0, currency: "X" }), "+0.00 X".to_string());
}

#[test]
fn plus_negative() {
    check!(r#"{:+} with -5 cents"#, format!("{:+}", Money { cents: -5, currency: "EUR" }), "-0.05 EUR".to_string());
}

#[test]
fn plus_and_width() {
    check!(r#"{:>+12}"#, format!("{:>+12}", Money { cents: 1234, currency: "USD" }), "  +12.34 USD".to_string());
}

#[test]
fn debug_pretty() {
    check!(r#"{:#?}"#, format!("{:#?}", Money { cents: -100, currency: "USD" }), "Money(\n    -1.00 USD,\n)".to_string());
}

#[test]
fn debug_in_a_vec() {
    check!(r#"{:?} of a Vec"#, format!("{:?}", vec![Money { cents: 100, currency: "A" }, Money { cents: -50, currency: "B" }]), "[Money(1.00 A), Money(-0.50 B)]".to_string());
}

#[test]
fn debug_pretty_nested() {
    check!(r#"{:#?} of Some(..)"#, format!("{:#?}", Some(Money { cents: 1, currency: "USD" })), "Some(\n    Money(\n        0.01 USD,\n    ),\n)".to_string());
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(7212);
    for _ in 0..300 {
        let cents = rng.int(-1_000_000_000_000, 1_000_000_000_000);
        let width = rng.below(24);
        let abs = cents.unsigned_abs();
        let digits = format!("{}.{}{} JPY", abs / 100, abs % 100 / 10, abs % 10);
        let plain = if cents < 0 { format!("-{digits}") } else { digits.clone() };
        let plus = if cents < 0 { plain.clone() } else { format!("+{digits}") };
        let padded = " ".repeat(width.saturating_sub(plain.len())) + &plain;
        let m = Money { cents, currency: "JPY" };
        check!(format!("cents = {cents}, {{:>{width}}}"),
               (format!("{m}"), format!("{m:>width$}"), format!("{m:+}"), format!("{m:?}")),
               (plain.clone(), padded, plus, format!("Money({plain})")));
    }
}
