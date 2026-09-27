use solution::*;

#[test]
fn fills() {
    let vars = std::collections::HashMap::from([("name", "Ada"), ("lang", "Rust")]);
    check!(r#""Hi {name}, welcome to {lang}!""#, render("Hi {name}, welcome to {lang}!", &vars), Ok("Hi Ada, welcome to Rust!".to_string()));
}

#[test]
fn escapes() {
    let vars = std::collections::HashMap::new();
    check!(r#""{{literal}}""#, render("{{literal}}", &vars), Ok("{literal}".to_string()));
}
