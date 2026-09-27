use solution::*;

#[test]
fn empty() {
    check!(r#"prices = []"#, max_profit(&[]), 0);
}

#[test]
fn late_low() {
    check!(r#"prices = [2, 4, 1]"#, max_profit(&[2, 4, 1]), 2);
}
