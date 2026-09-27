use solution::*;

#[test]
fn mid_char() {
    check!(r#""héllo", 5"#, truncate("héllo", 5), "h…".to_string());
}

#[test]
fn cjk() {
    check!(r#""日本語テキスト", 10"#, truncate("日本語テキスト", 10), "日本…".to_string());
}

#[test]
fn no_room() {
    check!(r#""abc", 2"#, truncate("abc", 2), String::new());
}

#[test]
fn exact_fit() {
    check!(r#""abcd", 4"#, truncate("abcd", 4), "abcd".to_string());
}
