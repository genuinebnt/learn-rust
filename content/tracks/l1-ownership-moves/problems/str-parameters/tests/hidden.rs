use solution::*;

#[test]
fn empty() {
    check!(r#""""#, initials(""), "");
}

#[test]
fn unicode() {
    check!(r#""élodie ünal""#, initials("élodie ünal"), "ÉÜ");
}
