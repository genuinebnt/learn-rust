use solution::*;

#[test]
fn after_with_temporary_prefix() {
    let line = String::from("key=value");
    let v = after(&line, &String::from("key="));
    check!(r#"after("key=value", a temporary "key=")"#, v, Some("value"));
}

#[test]
fn lookup_with_temporary_key() {
    let map = std::collections::HashMap::from([("a".to_string(), "1".to_string())]);
    let v = lookup(&map, &"a".to_string());
    check!(r#"map {a: 1}; lookup of a temporary "a""#, v, Some("1"));
}

#[test]
fn layered_local_wins() {
    const GLOBAL: &[(&str, &str)] = &[("color", "auto"), ("pager", "less")];
    let local = [("color", "never")];
    let layered = Layered { global: GLOBAL, local: &local };
    check!(r#"global {color: auto, pager: less}; local {color: never}"#, (layered.get("color"), layered.get("pager"), layered.get("x")), (Some("never"), Some("less"), None));
}

#[test]
fn layered_local_from_a_string() {
    const GLOBAL: &[(&str, &str)] = &[("color", "auto"), ("pager", "less")];
    let req = String::from("user=ann");
    let (k, v) = req.split_once('=').unwrap();
    let local = [(k, v)];
    let layered = Layered { global: GLOBAL, local: &local };
    check!(r#"local value borrowed from a request String"#, layered.get("user"), Some("ann"));
}

#[test]
fn or_default_example() {
    check!(r#"or_default(None, "d"), or_default(Some("v"), "d")"#, (or_default(None, "d"), or_default(Some("v"), "d")), ("d", "v"));
}
