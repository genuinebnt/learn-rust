use solution::*;

#[test]
fn literal() {
    check!(r#""Ada Lovelace""#, initials("Ada Lovelace"), "AL");
}

#[test]
fn from_string() {
    check!(r#"&String "grace brewster hopper""#, { let s = String::from("grace brewster hopper"); initials(&s) }, "GBH");
}
