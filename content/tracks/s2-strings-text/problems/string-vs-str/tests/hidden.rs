use solution::*;

#[test]
fn in_place() {
    let mut s = String::from("wow");
    exclaim(&mut s);
    exclaim(&mut s);
    check!(r#"exclaim twice on "wow""#, s, "wow!!".to_string());
}

#[test]
fn no_space() {
    check!(r#""single""#, first_word("single"), "single");
}

#[test]
fn leading_space() {
    check!(r#"" x""#, first_word(" x"), "");
}
