use solution::*;

#[test]
fn display() {
    check!(r#"12.34 USD"#, format!("{}", Money { cents: 1234, currency: "USD" }), "12.34 USD".to_string());
}

#[test]
fn negative_cents() {
    check!(r#"-5 cents"#, format!("{}", Money { cents: -5, currency: "EUR" }), "-0.05 EUR".to_string());
}
