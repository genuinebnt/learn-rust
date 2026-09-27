use solution::*;

#[test]
fn trims() {
    check!(r#""  a \n\n b\n""#, trimmed_lines("  a \n\n b\n"), vec!["a", "b"]);
}

#[test]
fn owned_input() {
    let input = String::from("x\n  y  ");
    check!(r#"input from a String: "x\n  y  ""#, trimmed_lines(&input), vec!["x", "y"]);
}
