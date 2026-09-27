use solution::*;

#[test]
fn equal() {
    check!(r#""  Rust ", "rust""#, { let (mut a, mut b) = ("  Rust ".to_string(), "rust".to_string()); (same_after_normalizing(&mut a, &mut b), a) }, (true, "rust".to_string()));
}

#[test]
fn both_trimmed() {
    check!(r#"" Go", "GO  ""#, { let (mut a, mut b) = (" Go".to_string(), "GO  ".to_string()); (same_after_normalizing(&mut a, &mut b), b) }, (true, "go".to_string()));
}
