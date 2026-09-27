use solution::*;

#[test]
fn one() {
    let input = String::from("x");
    check!(r#"input "x" from a String"#, all_names(&input).len(), 3);
}
