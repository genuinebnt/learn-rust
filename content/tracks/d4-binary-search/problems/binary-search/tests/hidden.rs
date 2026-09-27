use solution::*;

#[test]
fn empty() {
    check!(r#"[], 1"#, search(&[], 1), None);
}

#[test]
fn ends() {
    check!(r#"[1,2,3], 1 and 3"#, (search(&[1, 2, 3], 1), search(&[1, 2, 3], 3)), (Some(0), Some(2)));
}

#[test]
fn below_all() {
    check!(r#"[5], 1"#, search(&[5], 1), None);
}

#[test]
fn million() {
    let v: Vec<i32> = (0..1_000_000).map(|i| i * 2).collect();
    check!(r#"0..10⁶ evens, 777_778"#, search(&v, 777_778), Some(388_889));
}
