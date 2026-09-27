use solution::*;

fn s(x: &str) -> Json {
    Json::Str(x.to_string())
}

fn obj(fields: Vec<(&str, Json)>) -> Json {
    Json::Obj(fields.into_iter().map(|(k, v)| (k.to_string(), v)).collect())
}

/// {"users": [{"name": "Ada", "age": 36, "admin": true, "boss": null}, {"name": "Linus", "age": 54}],
///  "0": "zero", "": {"x": 1}, "dup": 1, "dup": 2, "count": 2, "none": null}
fn doc() -> Json {
    obj(vec![
        ("users", Json::Arr(vec![
            obj(vec![("name", s("Ada")), ("age", Json::Num(36.0)), ("admin", Json::Bool(true)), ("boss", Json::Null)]),
            obj(vec![("name", s("Linus")), ("age", Json::Num(54.0))]),
        ])),
        ("0", s("zero")),
        ("", obj(vec![("x", Json::Num(1.0))])),
        ("dup", Json::Num(1.0)),
        ("dup", Json::Num(2.0)),
        ("count", Json::Num(2.0)),
        ("none", Json::Null),
    ])
}

#[test]
fn nested_lookup() {
    check!(r#"doc, path = "users.1.name""#, get(&doc(), "users.1.name").cloned(), Some(s("Linus")));
}

#[test]
fn number_at_a_path() {
    check!(r#"doc, num_at("users.0.age"), num_at("users.0.name")"#, (num_at(&doc(), "users.0.age"), num_at(&doc(), "users.0.name")), (Some(36.0), None));
}

#[test]
fn empty_path_is_the_root() {
    let d = doc();
    check!(r#"doc, path = """#, get(&d, "") == Some(&d), true);
}

#[test]
fn index_out_of_range() {
    check!(r#"doc, path = "users.5""#, get(&doc(), "users.5").cloned(), None);
}

#[test]
fn missing_is_not_null() {
    check!(r#"doc, is_null_at("users.0.boss"), is_null_at("users.1.boss")"#, (is_null_at(&doc(), "users.0.boss"), is_null_at(&doc(), "users.1.boss")), (true, false));
}
