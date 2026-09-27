use solution::*;

/// A type from "another crate" whose Describe differs from its Display.
struct Celsius(f64);

impl std::fmt::Display for Celsius {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}

impl Describe for Celsius {
    fn describe(&self) -> String {
        format!("{}°C", self.0)
    }
}

#[test]
fn scalars() {
    check!(r#"42i32, 2.5f64, true, 'x'"#, (42i32.describe(), 2.5f64.describe(), true.describe(), 'x'.describe()), ("42".to_string(), "2.5".to_string(), "true".to_string(), "x".to_string()));
}

#[test]
fn strings_and_name() {
    check!(r#""hi", String "yo", Name("ADA")"#, ("hi".describe(), String::from("yo").describe(), Name("ADA".into()).describe()), ("hi".to_string(), "yo".to_string(), "ada".to_string()));
}

#[test]
fn vec_and_option() {
    check!(r#"vec![1, 2], Some(3), None"#, (vec![1, 2].describe(), Some(3).describe(), None::<i32>.describe()), ("[1, 2]".to_string(), "3".to_string(), "-".to_string()));
}

#[test]
fn nested_with_refs() {
    check!(r#"vec![Some("a"), None]"#, vec![Some("a"), None].describe(), "[a, -]");
}

#[test]
fn your_own_impl() {
    check!(r#"Celsius(21.5): Display is 21.5, Describe is 21.5°C"#, (Celsius(21.5).to_string(), vec![Celsius(21.5)].describe()), ("21.5".to_string(), "[21.5°C]".to_string()));
}
