use solution::*;

#[test]
fn repeats() {
    check!(r#"text = "a b a c a""#, word_counts("a b a c a"), std::collections::HashMap::from([("a", 3), ("b", 1), ("c", 1)]));
}

#[test]
fn empty() {
    check!(r#"text = """#, word_counts(""), std::collections::HashMap::new());
}

#[test]
fn one_word_twice() {
    check!(r#"text = "hi hi""#, word_counts("hi hi"), std::collections::HashMap::from([("hi", 2)]));
}

#[test]
fn case_sensitive() {
    check!(r#"text = "Go go""#, word_counts("Go go"), std::collections::HashMap::from([("Go", 1), ("go", 1)]));
}

#[test]
fn extra_whitespace() {
    check!(r#"text = " a  a ""#, word_counts(" a  a "), std::collections::HashMap::from([("a", 2)]));
}
