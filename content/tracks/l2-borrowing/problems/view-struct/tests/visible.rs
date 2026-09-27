use solution::*;

#[test]
fn views_together() {
    let mut d = Document { title: "Draft".to_string(), tags: vec![], lines: vec![], words: 0 };
    {
        let (mut h, mut b) = d.split();
        b.push_line("two words");
        h.retitle("Final");
    }
    check!(r#"split; push a line and retitle while both are alive"#, (d.title.as_str(), d.tags.clone(), d.lines.clone(), d.words), ("Final", vec!["edited".to_string()], vec!["two words".to_string()], 2));
}

#[test]
fn hashtags_example() {
    let mut d = Document { title: "Draft".to_string(), tags: vec![], lines: vec![], words: 0 };
    d.body().push_line("see #rust and #borrowck");
    d.body().push_line("#rust again #");
    check!(r##"lines "see #rust and #borrowck", "#rust again #""##, (hashtags(&mut d), d.tags.clone()), (2, vec!["rust".to_string(), "borrowck".to_string()]));
}

#[test]
fn retitle_tags_once() {
    let mut d = Document { title: "Draft".to_string(), tags: vec![], lines: vec![], words: 0 };
    d.header().retitle("A");
    d.header().retitle("B");
    check!(r#"retitle twice"#, (d.title.as_str(), d.tags.clone()), ("B", vec!["edited".to_string()]));
}

#[test]
fn tag_reports() {
    let mut d = Document { title: "Draft".to_string(), tags: vec![], lines: vec![], words: 0 };
    check!(r#"tag x, x, y"#, { let mut h = d.header(); (h.tag("x"), h.tag("x"), h.tag("y")) }, (true, false, true));
}

#[test]
fn word_count() {
    let mut d = Document { title: "Draft".to_string(), tags: vec![], lines: vec![], words: 0 };
    let mut b = d.body();
    b.push_line("a b  c");
    b.push_line("");
    b.push_line(" d ");
    check!(r#"push "a b  c", "", " d ""#, (d.words, d.lines.len()), (4, 3));
}
