use solution::*;

#[test]
fn owned_input() {
    let input = String::from("alice\nbob");
    check!(r#"input "alice\nbob" from a String"#, all_names(&input), vec!["alice", "bob", "root", "admin"]);
}

#[test]
fn empty() {
    check!(r#""""#, all_names(""), vec!["root", "admin"]);
}

#[test]
fn one() {
    let input = String::from("x");
    check!(r#"input "x" from a String"#, all_names(&input), vec!["x", "root", "admin"]);
}

#[test]
fn trailing_newline() {
    check!(r#""a\n""#, all_names("a\n"), vec!["a", "root", "admin"]);
}

#[test]
fn blank_line_kept() {
    check!(r#""a\n\nb""#, all_names("a\n\nb"), vec!["a", "", "b", "root", "admin"]);
}
