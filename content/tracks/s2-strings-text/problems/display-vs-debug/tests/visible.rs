use solution::*;

#[test]
fn display() {
    check!(r#"12.34 USD"#, format!("{}", Money { cents: 1234, currency: "USD" }), "12.34 USD".to_string());
}

#[test]
fn negative_cents() {
    check!(r#"-5 cents"#, format!("{}", Money { cents: -5, currency: "EUR" }), "-0.05 EUR".to_string());
}

#[test]
fn whole_amount() {
    check!(r#"500 cents"#, format!("{}", Money { cents: 500, currency: "USD" }), "5.00 USD".to_string());
}

#[test]
fn zero() {
    check!(r#"0 cents"#, format!("{}", Money { cents: 0, currency: "X" }), "0.00 X".to_string());
}

#[test]
fn right_aligned() {
    check!(r#"{:>10} then |"#, format!("{:>10}|", Money { cents: 99, currency: "EUR" }), "  0.99 EUR|".to_string());
}
