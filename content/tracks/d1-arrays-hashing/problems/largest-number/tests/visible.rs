use solution::*;

#[test]
fn two() {
    check!(r#"nums = [10, 2]"#, largest_number(&[10, 2]), "210");
}

#[test]
fn five() {
    check!(r#"nums = [3, 30, 34, 5, 9]"#, largest_number(&[3, 30, 34, 5, 9]), "9534330");
}
