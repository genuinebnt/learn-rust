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

#[test]
fn empty() {
    check!(r#""""#, trimmed_lines(""), Vec::<&str>::new());
}

#[test]
fn inner_spaces_kept() {
    check!(r#""  a b  ""#, trimmed_lines("  a b  "), vec!["a b"]);
}

#[test]
fn all_blank() {
    check!(r#"" \n\t\n""#, trimmed_lines(" \n\t\n").len(), 0);
}
