use solution::*;

#[test]
fn classic() {
    check!(r#"prices = [7, 1, 5, 3, 6, 4]"#, max_profit(&[7, 1, 5, 3, 6, 4]), 5);
}

#[test]
fn falling() {
    check!(r#"prices = [7, 6, 4, 3, 1]"#, max_profit(&[7, 6, 4, 3, 1]), 0);
}

#[test]
fn empty() {
    check!(r#"prices = []"#, max_profit(&[]), 0);
}

#[test]
fn single() {
    check!(r#"prices = [5]"#, max_profit(&[5]), 0);
}

#[test]
fn buy_before_sell() {
    check!(r#"prices = [2, 4, 1]"#, max_profit(&[2, 4, 1]), 2);
}
