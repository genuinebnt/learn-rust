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
fn digit_key_on_an_object() {
    check!(r#"doc, path = "0""#, get(&doc(), "0").cloned(), Some(s("zero")));
}

#[test]
fn empty_key_segment() {
    check!(r#"doc, path = ".x""#, num_at(&doc(), ".x"), Some(1.0));
}

#[test]
fn trailing_dot_on_an_array() {
    check!(r#"doc, path = "users.""#, get(&doc(), "users.").cloned(), None);
}

#[test]
fn plus_sign_is_not_an_index() {
    check!(r#"doc, path = "users.+1""#, get(&doc(), "users.+1").cloned(), None);
}

#[test]
fn leading_zero_index() {
    check!(r#"doc, path = "users.01.age""#, num_at(&doc(), "users.01.age"), Some(54.0));
}

#[test]
fn huge_index_does_not_panic() {
    check!(r#"doc, path = "users.99999999999999999999999""#, get(&doc(), "users.99999999999999999999999").cloned(), None);
}

#[test]
fn negative_index() {
    check!(r#"doc, path = "users.-1""#, get(&doc(), "users.-1").cloned(), None);
}

#[test]
fn path_through_a_scalar() {
    check!(r#"doc, path = "count.0" and "users.0.name.x""#, (get(&doc(), "count.0").cloned(), get(&doc(), "users.0.name.x").cloned()), (None, None));
}

#[test]
fn path_through_null() {
    check!(r#"doc, path = "none.x""#, get(&doc(), "none.x").cloned(), None);
}

#[test]
fn first_duplicate_key_wins() {
    check!(r#"doc, path = "dup""#, num_at(&doc(), "dup"), Some(1.0));
}

#[test]
fn null_at_the_top() {
    check!(r#"doc, is_null_at("none"), is_null_at("nope"), is_null_at("")"#, (is_null_at(&doc(), "none"), is_null_at(&doc(), "nope"), is_null_at(&doc(), "")), (true, false, false));
}

#[test]
fn scalar_root() {
    check!(r#"root = 7, path = "" and "a""#, (num_at(&Json::Num(7.0), ""), get(&Json::Num(7.0), "a")), (Some(7.0), None));
}

#[test]
fn num_at_on_a_bool() {
    check!(r#"doc, num_at("users.0.admin")"#, num_at(&doc(), "users.0.admin"), None);
}

#[test]
fn unicode_key() {
    check!(r#"{"ключ": [true]}, path = "ключ.0""#, get(&obj(vec![("ключ", Json::Arr(vec![Json::Bool(true)]))]), "ключ.0").cloned(), Some(Json::Bool(true)));
}

#[test]
fn borrows_from_the_root() {
    let d = doc();
    check!(r#"doc, path = "users.0""#, std::ptr::eq(get(&d, "users.0").unwrap(), match &d { Json::Obj(f) => match &f[0].1 { Json::Arr(a) => &a[0], _ => unreachable!() }, _ => unreachable!() }), true);
}

fn brute<'a>(node: &'a Json, segs: &[&str]) -> Option<&'a Json> {
    let Some((first, rest)) = segs.split_first() else {
        return Some(node);
    };
    let next = match node {
        Json::Obj(fields) => fields.iter().find(|(k, _)| k == first).map(|(_, v)| v),
        Json::Arr(items) if !first.is_empty() && first.chars().all(|c| c.is_ascii_digit()) && first.len() < 5 => items.get(first.parse::<usize>().unwrap()),
        _ => None,
    };
    brute(next?, rest)
}

fn random_json(rng: &mut anneal_prelude::Rng, depth: usize) -> Json {
    let kind = if depth == 0 { rng.below(3) } else { rng.below(6) };
    match kind {
        0 => Json::Null,
        1 => Json::Num(rng.int(-3, 3) as f64),
        2 => Json::Str("s".to_string()),
        3 | 4 => {
            let n = rng.below(4);
            let mut fields = Vec::new();
            for _ in 0..n {
                let k = rng.pick(&["a", "b", "0", "1", ""]).to_string();
                fields.push((k, random_json(rng, depth - 1)));
            }
            Json::Obj(fields)
        }
        _ => {
            let n = rng.below(4);
            let mut items = Vec::new();
            for _ in 0..n {
                items.push(random_json(rng, depth - 1));
            }
            Json::Arr(items)
        }
    }
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(7102);
    for _ in 0..400 {
        let root = random_json(&mut rng, 3);
        let n = rng.below(4);
        let mut segs: Vec<&str> = Vec::new();
        for _ in 0..n {
            segs.push(*rng.pick(&["a", "b", "0", "1", "2", "", "+1", "01"]));
        }
        let path = segs.join(".");
        let want = if path.is_empty() { Some(&root) } else { brute(&root, &segs) };
        let desc = format!("root = {root:?}, path = {path:?}");
        check!(desc.clone(), get(&root, &path), want);
        check!(format!("num_at, {desc}"), num_at(&root, &path), match want { Some(Json::Num(x)) => Some(*x), _ => None });
        check!(format!("is_null_at, {desc}"), is_null_at(&root, &path), want == Some(&Json::Null));
    }
}

#[test]
fn deep_path() {
    let mut root = Json::Num(42.0);
    for i in 0..1000 {
        root = if i % 2 == 0 { Json::Arr(vec![Json::Null, root]) } else { obj(vec![("k", root)]) };
    }
    let path = vec!["k", "1"].repeat(500).join(".");
    check!("1000 levels, alternating arrays and objects", num_at(&root, &path), Some(42.0));
}
