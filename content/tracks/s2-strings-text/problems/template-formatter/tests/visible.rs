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

#[test]
fn no_placeholders() {
    let vars = std::collections::HashMap::new();
    check!(r#""plain text""#, render("plain text", &vars), Ok("plain text".to_string()));
}

#[test]
fn closing_escape() {
    let vars = std::collections::HashMap::new();
    check!(r#""}} and {{""#, render("}} and {{", &vars), Ok("} and {".to_string()));
}

#[test]
fn same_name_twice() {
    let vars = std::collections::HashMap::from([("a", "1")]);
    check!(r#""{a}-{a}", a = "1""#, render("{a}-{a}", &vars), Ok("1-1".to_string()));
}
