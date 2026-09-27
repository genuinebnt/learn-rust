use solution::*;

#[test]
fn creates_and_reuses() {
    check!(r#"push 1 then 2 under "a""#, { let mut m = std::collections::HashMap::new(); get_or_create(&mut m, "a").push(1); get_or_create(&mut m, "a").push(2); m["a"].clone() }, vec![1, 2]);
}

#[test]
fn existing_kept() {
    check!(r#""k" already maps to [9]"#, { let mut m = std::collections::HashMap::from([("k".to_string(), vec![9])]); get_or_create(&mut m, "k").push(1); m["k"].clone() }, vec![9, 1]);
}
