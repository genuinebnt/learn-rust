use solution::*;

#[test]
fn whitespace() {
    check!(r#"text = "  x\n x\tx  ""#, word_counts("  x\n x\tx  "), std::collections::HashMap::from([("x", 3)]));
}
