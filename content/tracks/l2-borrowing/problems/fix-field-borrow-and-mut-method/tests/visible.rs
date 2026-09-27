use solution::*;

#[test]
fn saves() {
    check!(r#"text "ab", append "c""#, { let mut e = Editor { text: "ab".into(), history: vec![] }; e.append("c"); (e.text, e.history) }, ("abc".to_string(), vec!["ab".to_string()]));
}

#[test]
fn empty_append() {
    check!(r#"text "a", append """#, { let mut e = Editor { text: "a".into(), history: vec![] }; e.append(""); (e.text, e.history.len()) }, ("a".to_string(), 1));
}
