use solution::*;

#[test]
fn preview_ascii() {
    check!(r#""hello world", 5"#, preview("hello world", 5), "hello…".to_string());
}

#[test]
fn preview_accented() {
    check!(r#""héllo wörld", 2"#, preview("héllo wörld", 2), "hé…".to_string());
}

#[test]
fn preview_fits() {
    check!(r#""short", 10"#, preview("short", 10), "short".to_string());
}

#[test]
fn capitalize_accented() {
    check!(r#""école""#, capitalize("école"), "École".to_string());
}

#[test]
fn mask_card() {
    check!(r#""4111111111111111""#, mask("4111111111111111"), "************1111".to_string());
}
