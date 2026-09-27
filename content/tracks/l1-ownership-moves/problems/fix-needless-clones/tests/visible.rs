use solution::*;

#[test]
fn search() {
    let lib = Library::new(vec!["Dune".into(), "Dune Messiah".into(), "Emma".into()]);
    check!(r#"books = ["Dune", "Dune Messiah", "Emma"], needle = "Dune""#, lib.search("Dune"), vec!["Dune", "Dune Messiah"]);
}

#[test]
fn longest() {
    let lib = Library::new(vec!["Dune".into(), "Dune Messiah".into(), "Emma".into()]);
    check!(r#"books = ["Dune", "Dune Messiah", "Emma"]"#, lib.longest(), Some("Dune Messiah"));
}

#[test]
fn count_with() {
    let lib = Library::new(vec!["Dune".into(), "Dune Messiah".into(), "Emma".into()]);
    check!(r#"books = ["Dune", "Dune Messiah", "Emma"], needle = "Dune""#, lib.count_with("Dune"), 2);
}

#[test]
fn longest_tie_is_last() {
    let lib = Library::new(vec!["ab".into(), "cd".into(), "e".into()]);
    check!(r#"books = ["ab", "cd", "e"]"#, lib.longest(), Some("cd"));
}

#[test]
fn longest_no_books() {
    let lib = Library::new(vec![]);
    check!(r#"books = []"#, lib.longest(), None);
}
