use solution::*;

#[test]
fn interleaved() {
    check!(r#""([)]""#, is_valid("([)]"), false);
}

#[test]
fn unclosed() {
    check!(r#""((""#, is_valid("(("), false);
}

#[test]
fn close_first() {
    check!(r#"")""#, is_valid(")"), false);
}

#[test]
fn empty() {
    check!(r#""""#, is_valid(""), true);
}

#[test]
fn deep() {
    let s = format!("{}{}", "(".repeat(100_000), ")".repeat(100_000));
    check!(r#"10⁵ nested pairs"#, is_valid(&s), true);
}
