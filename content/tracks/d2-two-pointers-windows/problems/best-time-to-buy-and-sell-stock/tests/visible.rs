use solution::*;

#[test]
fn classic() {
    check!(r#"prices = [7, 1, 5, 3, 6, 4]"#, max_profit(&[7, 1, 5, 3, 6, 4]), 5);
}

#[test]
fn falling() {
    check!(r#"prices = [7, 6, 4, 3, 1]"#, max_profit(&[7, 6, 4, 3, 1]), 0);
}
