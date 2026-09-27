use solution::*;

#[test]
fn saves() {
    check!(r#"text "ab", append "c""#, { let mut e = Editor { text: "ab".into(), history: vec![] }; e.append("c"); (e.text, e.history) }, ("abc".to_string(), vec!["ab".to_string()]));
}

#[test]
fn empty_append() {
    check!(r#"text "a", append """#, { let mut e = Editor { text: "a".into(), history: vec![] }; e.append(""); (e.text, e.history.len()) }, ("a".to_string(), 1));
}

#[test]
fn unicode() {
    check!(r#"text "é", append "ß""#, { let mut e = Editor { text: "é".into(), history: vec![] }; e.append("ß"); (e.text, e.history) }, ("éß".to_string(), vec!["é".to_string()]));
}

#[test]
fn existing_history() {
    check!(r#"history ["old"], text "t", append "x""#, { let mut e = Editor { text: "t".into(), history: vec!["old".into()] }; e.append("x"); e.history }, vec!["old".to_string(), "t".to_string()]);
}

#[test]
fn twice() {
    check!(r#"append "x" then "y""#, { let mut e = Editor { text: String::new(), history: vec![] }; e.append("x"); e.append("y"); e.history }, vec![String::new(), "x".to_string()]);
}
