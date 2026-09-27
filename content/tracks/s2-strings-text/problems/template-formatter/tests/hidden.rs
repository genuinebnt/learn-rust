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

#[test]
fn value_not_rerendered() {
    let vars = std::collections::HashMap::from([("a", "{b}"), ("b", "no")]);
    check!(r#""{a}", a = "{b}""#, render("{a}", &vars), Ok("{b}".to_string()));
}

#[test]
fn escaped_name() {
    let vars = std::collections::HashMap::from([("name", "Ada")]);
    check!(r#""{{name}}""#, render("{{name}}", &vars), Ok("{name}".to_string()));
}

#[test]
fn unclosed_after_unicode() {
    let vars = std::collections::HashMap::new();
    check!(r#""é{x""#, render("é{x", &vars), Err(TemplateError::Unclosed(2)));
}

#[test]
fn stray_at_end() {
    let vars = std::collections::HashMap::new();
    check!(r#""abc}""#, render("abc}", &vars), Err(TemplateError::StrayBrace(3)));
}

#[test]
fn three_closing() {
    let vars = std::collections::HashMap::new();
    check!(r#""}}}""#, render("}}}", &vars), Err(TemplateError::StrayBrace(2)));
}

#[test]
fn braces_around_placeholder() {
    let vars = std::collections::HashMap::from([("a", "1")]);
    check!(r#""{{{a}}}", a = "1""#, render("{{{a}}}", &vars), Ok("{1}".to_string()));
}

#[test]
fn empty_template() {
    let vars = std::collections::HashMap::new();
    check!(r#""""#, render("", &vars), Ok(String::new()));
}

#[test]
fn spaces_in_name() {
    let vars = std::collections::HashMap::from([("a", "1")]);
    check!(r#""{ a }""#, render("{ a }", &vars), Err(TemplateError::Unknown(" a ".to_string())));
}

#[test]
fn unicode_name_and_value() {
    let vars = std::collections::HashMap::from([("名前", "太郎")]);
    check!(r#""{名前}さん", 名前 = "太郎""#, render("{名前}さん", &vars), Ok("太郎さん".to_string()));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2218);
    let vars = std::collections::HashMap::from([("a", "1"), ("bb", "22")]);
    let pieces = [("{a}", "1"), ("{bb}", "22"), ("{{", "{"), ("}}", "}"), ("x", "x"), ("é", "é")];
    for _ in 0..400 {
        let mut template = String::new();
        let mut want = String::new();
        for _ in 0..rng.below(8) {
            let (t, w) = *rng.pick(&pieces);
            template += t;
            want += w;
        }
        let want = if rng.below(4) == 0 {
            let at = template.len();
            template.push('}');
            Err(TemplateError::StrayBrace(at))
        } else {
            Ok(want)
        };
        check!(format!("template = {template:?}, vars = {{a: 1, bb: 22}}"), render(&template, &vars), want);
    }
}

#[test]
fn scale_200k_placeholders() {
    let vars = std::collections::HashMap::from([("a", "x")]);
    let template = "{a}".repeat(200_000);
    check!("template = \"{a}{a}…\" (200000 placeholders)", render(&template, &vars).map(|s| s.len()), Ok(200_000));
}
