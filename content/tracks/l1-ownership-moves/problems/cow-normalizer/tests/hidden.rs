use solution::*;

#[test]
fn tabs_owned() {
    check!(r#""\t""#, matches!(normalize("\t"), std::borrow::Cow::Owned(_)), true);
}

#[test]
fn empty() {
    check!(r#""""#, normalize(""), "");
}
