use solution::*;

#[test]
fn longest_outlives_doc() {
    let text = String::from("a\nlonger line\nb");
    let line;
    {
        let doc = Document::new(&text);
        line = doc.longest_line();
    }
    check!(r#"text "a\nlonger line\nb"; drop the Document"#, line, "longer line");
}

#[test]
fn lines_outlive_doc() {
    let text = String::from("x1\nno\n2x");
    let found;
    {
        let doc = Document::new(&text);
        found = doc.lines_with("x");
    }
    check!(r#"lines with "x"; drop the Document"#, found, vec!["x1", "2x"]);
}

#[test]
fn tie() {
    check!(r#""ab\ncd""#, Document::new("ab\ncd").longest_line(), "ab");
}

#[test]
fn empty_text() {
    let d = Document::new("");
    check!(r#""""#, (d.longest_line(), d.lines_with("x")), ("", Vec::<&str>::new()));
}

#[test]
fn no_line_matches() {
    check!(r#""a\nb", word "z""#, Document::new("a\nb").lines_with("z"), Vec::<&str>::new());
}
