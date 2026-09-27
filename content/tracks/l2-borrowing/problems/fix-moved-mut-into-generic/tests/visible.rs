use solution::*;

#[test]
fn twice() {
    check!(r#"s = "ab""#, { let mut o = String::new(); write_twice(&mut o, "ab"); o }, "abab".to_string());
}

#[test]
fn keeps_existing() {
    check!(r#"out = "x", s = "y""#, { let mut o = String::from("x"); write_twice(&mut o, "y"); o }, "xyy".to_string());
}
