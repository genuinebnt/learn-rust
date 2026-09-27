use solution::*;

#[test]
fn twice() {
    check!(r#"s = "ab""#, { let mut o = String::new(); write_twice(&mut o, "ab"); o }, "abab".to_string());
}

#[test]
fn keeps_existing() {
    check!(r#"out = "x", s = "y""#, { let mut o = String::from("x"); write_twice(&mut o, "y"); o }, "xyy".to_string());
}

#[test]
fn unicode() {
    check!(r#"s = "é""#, { let mut o = String::new(); write_twice(&mut o, "é"); o }, "éé".to_string());
}

#[test]
fn called_twice() {
    check!(r#"write "ab" twice, twice"#, { let mut o = String::new(); write_twice(&mut o, "ab"); write_twice(&mut o, "ab"); o }, "abababab".to_string());
}

#[test]
fn empty() {
    check!(r#"s = """#, { let mut o = String::from("z"); write_twice(&mut o, ""); o }, "z".to_string());
}
