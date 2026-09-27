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

#[test]
fn number_then_rest() {
    let mut c = Cursor::new(" 42 rest");
    check!(r#"" 42 rest": number, rest"#, (c.number(), c.rest()), (Some(42), " rest"));
}

#[test]
fn empty_source() {
    let mut c = Cursor::new("");
    check!(r#""": number, ident, rest"#, (c.number(), c.ident(), c.rest()), (None, None, ""));
}

#[test]
fn failure_keeps_position() {
    let mut c = Cursor::new("  x");
    check!(r#""  x": number fails, rest is unchanged"#, (c.number(), c.rest()), (None, "  x"));
}
