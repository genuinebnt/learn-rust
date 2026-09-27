use solution::*;

#[test]
fn equal() {
    check!(r#""  Rust ", "rust""#, { let (mut a, mut b) = ("  Rust ".to_string(), "rust".to_string()); (same_after_normalizing(&mut a, &mut b), a) }, (true, "rust".to_string()));
}

#[test]
fn both_trimmed() {
    check!(r#"" Go", "GO  ""#, { let (mut a, mut b) = (" Go".to_string(), "GO  ".to_string()); (same_after_normalizing(&mut a, &mut b), b) }, (true, "go".to_string()));
}

#[test]
fn normalize_only() {
    check!(r#""  MiXeD  ""#, { let mut s = "  MiXeD  ".to_string(); normalize(&mut s); s }, "mixed".to_string());
}

#[test]
fn inner_spaces_kept() {
    check!(r#""a  b", "a b""#, { let (mut a, mut b) = ("a  b".to_string(), "a b".to_string()); same_after_normalizing(&mut a, &mut b) }, false);
}

#[test]
fn empty_strings() {
    check!(r#""", """#, { let (mut a, mut b) = (String::new(), String::new()); (same_after_normalizing(&mut a, &mut b), a) }, (true, String::new()));
}
