use solution::*;

#[test]
fn pieces() {
    check!(r#""a,b,,c", ','"#, split_on("a,b,,c", ',').collect::<Vec<_>>(), vec!["a", "b", "", "c"]);
}

#[test]
fn empty_input() {
    check!(r#""", ','"#, split_on("", ',').collect::<Vec<_>>(), vec![""]);
}
