use solution::*;

#[test]
fn pieces() {
    check!(r#""a,b,,c", ','"#, split_on("a,b,,c", ',').collect::<Vec<_>>(), vec!["a", "b", "", "c"]);
}

#[test]
fn empty_input() {
    check!(r#""", ','"#, split_on("", ',').collect::<Vec<_>>(), vec![""]);
}

#[test]
fn no_delimiter() {
    check!(r#""abc", ','"#, split_on("abc", ',').collect::<Vec<_>>(), vec!["abc"]);
}

#[test]
fn only_delimiter() {
    check!(r#"",", ','"#, split_on(",", ',').collect::<Vec<_>>(), vec!["", ""]);
}

#[test]
fn from_the_back() {
    check!(r#""a,b", ',' reversed"#, split_on("a,b", ',').rev().collect::<Vec<_>>(), vec!["b", "a"]);
}
