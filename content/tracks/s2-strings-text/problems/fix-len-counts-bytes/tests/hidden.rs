use solution::*;

#[test]
fn odd() {
    check!(r#""abc", 6, '-'"#, center("abc", 6, '-'), "-abc--".to_string());
}

#[test]
fn too_wide() {
    check!(r#""日本語", 3, ' '"#, center("日本語", 3, ' '), "日本語".to_string());
}

#[test]
fn multibyte_fill() {
    check!(r#""x", 3, '·'"#, center("x", 3, '·'), "·x·".to_string());
}
