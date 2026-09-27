use solution::*;

#[test]
fn get_past_len() {
    check!(r#"push 1 item"#, { let mut v = SmallVec4::new(); v.push('a'); (v.get(1).copied(), v.get(0).copied()) }, (None, Some('a')));
}

#[test]
fn strings() {
    check!(r#"push 6 Strings"#, { let mut v = SmallVec4::new(); for w in ["a", "b", "c", "d", "e", "f"] { v.push(w.to_string()); } v.get(5).cloned() }, Some("f".to_string()));
}
