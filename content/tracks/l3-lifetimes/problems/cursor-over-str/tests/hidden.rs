use solution::*;

#[test]
fn overflow() {
    check!(r#""99999999999999999999""#, Cursor::new("99999999999999999999").number(), None);
}

#[test]
fn digit_first() {
    let mut c = Cursor::new("9abc");
    check!(r#""9abc": ident, then number, then ident"#, (c.ident(), c.number(), c.ident()), (None, Some(9), Some("abc")));
}

#[test]
fn underscore() {
    check!(r#""_x1 rest""#, Cursor::new("_x1 rest").ident(), Some("_x1"));
}

#[test]
fn unicode_after() {
    let mut c = Cursor::new("n é");
    check!(r#""n é": ident, rest"#, (c.ident(), c.rest()), (Some("n"), " é"));
}
