use solution::*;

fn profile(name: &str, nickname: Option<&str>, labels: &[(u32, &str)]) -> Profile {
    let mut p = Profile::new(name, nickname);
    for &(id, l) in labels {
        p.labels.insert(id, l.to_string());
    }
    p
}

#[test]
fn greeting_with_literals() {
    check!(r#"greeting("Ada", Some("ace")), greeting("Ada", None)"#, (greeting("Ada", Some("ace")), greeting("Ada", None)), ("Hello, ace!".to_string(), "Hello, Ada!".to_string()));
}

#[test]
fn greeting_from_a_profile() {
    let p = profile("Ada", Some("ace"), &[]);
    check!(r#"profile Ada / ace"#, greeting(&p.name, p.nickname()), "Hello, ace!".to_string());
}

#[test]
fn nickname_compares_to_a_literal() {
    let p = profile("Ada", Some("ace"), &[]);
    let q = profile("Ada", None, &[]);
    check!(r#"profile Ada / ace, and Ada / none"#, (p.nickname() == Some("ace"), q.nickname()), (true, None));
}

#[test]
fn label_lookup() {
    let p = profile("Ada", None, &[(1, "one")]);
    check!(r#"labels {1: "one"}, label(1), label(2)"#, (p.label(1), p.label(2)), (Some("one"), None));
}

#[test]
fn label_or_with_a_literal_default() {
    let p = profile("Ada", None, &[(1, "one")]);
    check!(r#"labels {1: "one"}, label_or(1, "?"), label_or(7, "?")"#, (label_or(&p, 1, "?"), label_or(&p, 7, "?")), ("one", "?"));
}
