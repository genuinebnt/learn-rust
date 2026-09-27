use solution::*;

#[test]
fn empty() {
    check!(r#"[]"#, largest_rectangle(&[]), 0);
}

#[test]
fn flat() {
    check!(r#"[3,3,3]"#, largest_rectangle(&[3, 3, 3]), 9);
}

#[test]
fn valley() {
    check!(r#"[5,0,5]"#, largest_rectangle(&[5, 0, 5]), 5);
}

#[test]
fn huge() {
    let h = vec![1_000_000_000u32; 100_000];
    check!(r#"10⁵ bars of height 10⁹"#, largest_rectangle(&h), 100_000_000_000_000);
}
