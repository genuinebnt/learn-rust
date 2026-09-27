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
