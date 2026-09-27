use solution::*;

#[test]
fn tokens() {
    let mut c = Cursor::new("  let x = 42");
    check!(r#""  let x = 42": ident, ident, number, rest"#, (c.ident(), c.ident(), c.number(), c.rest()), (Some("let"), Some("x"), None, " = 42"));
}

#[test]
fn outlives_cursor() {
    let src = String::from("alpha 7");
    let id;
    {
        let mut c = Cursor::new(&src);
        id = c.ident();
    }
    check!(r#"ident read, then the cursor is dropped"#, id, Some("alpha"));
}
