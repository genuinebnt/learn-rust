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
