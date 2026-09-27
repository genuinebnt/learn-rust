use solution::*;

#[test]
fn unknown() {
    let vars = std::collections::HashMap::from([("name", "Ada")]);
    check!(r#""{missing}""#, render("{missing}", &vars), Err(TemplateError::Unknown("missing".to_string())));
}

#[test]
fn unclosed() {
    let vars = std::collections::HashMap::from([("name", "Ada")]);
    check!(r#""oops {name""#, render("oops {name", &vars), Err(TemplateError::Unclosed(5)));
}

#[test]
fn stray() {
    let vars = std::collections::HashMap::new();
    check!(r#""a } b""#, render("a } b", &vars), Err(TemplateError::StrayBrace(2)));
}

#[test]
fn unicode_offsets() {
    let vars = std::collections::HashMap::new();
    check!(r#""é}""#, render("é}", &vars), Err(TemplateError::StrayBrace(2)));
}

#[test]
fn adjacent() {
    let vars = std::collections::HashMap::from([("a", "1"), ("b", "2")]);
    check!(r#""{a}{b}{{""#, render("{a}{b}{{", &vars), Ok("12{".to_string()));
}

#[test]
fn empty_name() {
    let vars = std::collections::HashMap::new();
    check!(r#""{}""#, render("{}", &vars), Err(TemplateError::Unknown(String::new())));
}
