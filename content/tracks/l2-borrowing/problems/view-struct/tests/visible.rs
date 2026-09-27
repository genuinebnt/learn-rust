use solution::*;

#[test]
fn retitles() {
    check!(r#"title "old""#, { let mut d = Document { title: "old".into(), body: "text".into(), tags: vec![] }; d.header().retitle("new"); (d.title, d.tags, d.body) }, ("new".to_string(), vec!["edited".to_string()], "text".to_string()));
}

#[test]
fn keeps_tags() {
    check!(r#"tags ["draft"]"#, { let mut d = Document { title: "t".into(), body: String::new(), tags: vec!["draft".into()] }; d.header().retitle("u"); d.tags }, vec!["draft".to_string(), "edited".to_string()]);
}

#[test]
fn shorter_title() {
    check!(r#"title "abc", retitle "x""#, { let mut d = Document { title: "abc".into(), body: String::new(), tags: vec![] }; d.header().retitle("x"); d.title }, "x".to_string());
}

#[test]
fn empty_title() {
    check!(r#"retitle """#, { let mut d = Document { title: "t".into(), body: String::new(), tags: vec![] }; d.header().retitle(""); (d.title, d.tags) }, (String::new(), vec!["edited".to_string()]));
}

#[test]
fn twice() {
    check!(r#"retitle twice"#, { let mut d = Document { title: String::new(), body: String::new(), tags: vec![] }; let mut h = d.header(); h.retitle("a"); h.retitle("b"); d.tags.len() }, 2);
}
