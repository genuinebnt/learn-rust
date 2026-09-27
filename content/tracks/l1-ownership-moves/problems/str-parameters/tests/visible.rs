use solution::*;

#[test]
fn literal() {
    check!(r#""Ada Lovelace""#, initials("Ada Lovelace"), "AL");
}

#[test]
fn from_string() {
    check!(r#"&String "grace brewster hopper""#, { let s = String::from("grace brewster hopper"); initials(&s) }, "GBH");
}

#[test]
fn single_word() {
    check!(r#""plato""#, initials("plato"), "P");
}

#[test]
fn extra_spaces_visible() {
    check!(r#"" grace  hopper ""#, initials(" grace  hopper "), "GH");
}

#[test]
fn all_lowercase() {
    check!(r#""alan mathison turing""#, initials("alan mathison turing"), "AMT");
}
