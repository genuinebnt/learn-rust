use solution::*;

#[test]
fn two() {
    check!(r#"nums = [10, 2]"#, largest_number(&[10, 2]), "210");
}

#[test]
fn five() {
    check!(r#"nums = [3, 30, 34, 5, 9]"#, largest_number(&[3, 30, 34, 5, 9]), "9534330");
}

#[test]
fn single_digit() {
    check!(r#"nums = [1]"#, largest_number(&[1]), "1");
}

#[test]
fn zeros() {
    check!(r#"nums = [0, 0]"#, largest_number(&[0, 0]), "0");
}

#[test]
fn three_thirty() {
    check!(r#"nums = [3, 30]"#, largest_number(&[3, 30]), "330");
}
