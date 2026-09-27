use solution::*;

#[test]
fn zeros() {
    check!(r#"nums = [0, 0]"#, largest_number(&[0, 0]), "0");
}

#[test]
fn shared_prefix() {
    check!(r#"nums = [121, 12]"#, largest_number(&[121, 12]), "12121");
}
