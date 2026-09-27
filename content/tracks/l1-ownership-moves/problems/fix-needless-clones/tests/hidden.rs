use solution::*;

#[test]
fn longest_tie_last() {
    let lib = Library::new(vec!["ab".into(), "cd".into()]);
    check!(r#"books = ["ab", "cd"]"#, lib.longest(), Some("cd"));
}

#[test]
fn count() {
    check!(r#"needle = "e""#, Library::new(vec!["Dune".into(), "Emma".into(), "Tess".into()]).count_with("e"), 2);
}

#[test]
fn empty() {
    let lib = Library::new(vec![]);
    check!(r#"no books"#, lib.longest(), None);
}
