use solution::*;

#[test]
fn retitles() {
    check!(r#"title "old""#, { let mut d = Document { title: "old".into(), body: "text".into(), tags: vec![] }; d.header().retitle("new"); (d.title, d.tags, d.body) }, ("new".to_string(), vec!["edited".to_string()], "text".to_string()));
}

#[test]
fn keeps_tags() {
    check!(r#"tags ["draft"]"#, { let mut d = Document { title: "t".into(), body: String::new(), tags: vec!["draft".into()] }; d.header().retitle("u"); d.tags }, vec!["draft".to_string(), "edited".to_string()]);
}
