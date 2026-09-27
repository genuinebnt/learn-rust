use solution::*;

#[test]
fn unicode_title() {
    check!(r#"retitle "日本""#, { let mut d = Document { title: "t".into(), body: String::new(), tags: vec![] }; d.header().retitle("日本"); d.title }, "日本".to_string());
}

#[test]
fn header_fields_point_into_doc() {
    check!(r#"push through the header's fields"#, { let mut d = Document { title: "a".into(), body: String::new(), tags: vec![] }; let h = d.header(); h.title.push_str("!"); h.tags.push("t".into()); (d.title, d.tags) }, ("a!".to_string(), vec!["t".to_string()]));
}

#[test]
fn body_untouched() {
    check!(r#"body "keep""#, { let mut d = Document { title: "t".into(), body: "keep".into(), tags: vec![] }; d.header().retitle("u"); d.body }, "keep".to_string());
}

#[test]
fn twice_last_wins() {
    check!(r#"retitle "a" then "b""#, { let mut d = Document { title: String::new(), body: String::new(), tags: vec![] }; let mut h = d.header(); h.retitle("a"); h.retitle("b"); (d.title, d.tags) }, ("b".to_string(), vec!["edited".to_string(), "edited".to_string()]));
}

#[test]
fn existing_tags_order() {
    check!(r#"tags ["x", "y"]"#, { let mut d = Document { title: String::new(), body: String::new(), tags: vec!["x".into(), "y".into()] }; d.header().retitle("t"); d.tags }, vec!["x".to_string(), "y".to_string(), "edited".to_string()]);
}

#[test]
fn same_title() {
    check!(r#"title "t", retitle "t""#, { let mut d = Document { title: "t".into(), body: String::new(), tags: vec![] }; d.header().retitle("t"); d.title }, "t".to_string());
}

#[test]
fn long_title() {
    check!(r#"retitle with 1000 chars"#, { let mut d = Document { title: "old".into(), body: String::new(), tags: vec![] }; let t = "z".repeat(1000); d.header().retitle(&t); d.title.len() }, 1000);
}

#[test]
fn body_readable_after() {
    check!(r#"body stays usable"#, { let mut d = Document { title: String::new(), body: "b".into(), tags: vec![] }; { let mut h = d.header(); h.retitle("n"); } d.body.push_str("!"); d.body }, "b!".to_string());
}
