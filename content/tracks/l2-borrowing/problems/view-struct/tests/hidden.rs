use solution::*;

#[test]
fn twice() {
    check!(r#"retitle twice"#, { let mut d = Document { title: String::new(), body: String::new(), tags: vec![] }; let mut h = d.header(); h.retitle("a"); h.retitle("b"); d.tags.len() }, 2);
}
