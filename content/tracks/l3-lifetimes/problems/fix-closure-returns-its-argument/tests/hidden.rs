use solution::*;

#[test]
fn all_blank() {
    check!(r#"" \n\t\n""#, trimmed_lines(" \n\t\n").len(), 0);
}
