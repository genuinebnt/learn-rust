use solution::*;

#[test]
fn excerpts_example() {
    let docs = ["Intro\n\nfirst words", " Notes \r\n body\r\n"].map(String::from);
    check!(r#"["Intro\n\nfirst words", " Notes \r\n body\r\n"]"#, excerpts(&docs), vec![Excerpt { title: "Intro", first_line: "first words" }, Excerpt { title: "Notes", first_line: "body" }]);
}

#[test]
fn body_excerpt_example() {
    check!(r#""meta\n---\nTitle\ntext""#, body_excerpt("meta\n---\nTitle\ntext"), Excerpt { title: "Title", first_line: "text" });
}

#[test]
fn body_without_separator() {
    check!(r#""Just\none""#, body_excerpt("Just\none"), Excerpt { title: "Just", first_line: "one" });
}

#[test]
fn biggest_first_on_tie() {
    let docs = ["a\nb", "c\nd", "e"].map(String::from);
    check!(r#"["a\nb", "c\nd", "e"]"#, biggest(&docs), Some(Excerpt { title: "a", first_line: "b" }));
}

#[test]
fn titles_longest_first() {
    let docs = ["ab", "abcd", "xy"].map(String::from);
    check!(r#"["ab", "abcd", "xy"]"#, titles(&docs), vec!["abcd", "ab", "xy"]);
}

#[test]
fn excerpts_borrow_the_docs() {
    let docs = [" T"].map(String::from);
    check!(r#"the title points into the document"#, excerpts(&docs)[0].title.as_ptr() == docs[0][1..].as_ptr(), true);
}
