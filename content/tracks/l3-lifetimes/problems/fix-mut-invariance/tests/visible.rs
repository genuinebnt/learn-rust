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
