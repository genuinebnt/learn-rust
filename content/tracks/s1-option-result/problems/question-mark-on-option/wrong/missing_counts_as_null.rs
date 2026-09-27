#[derive(Debug, Clone, PartialEq)]
pub enum Json {
    Null,
    Bool(bool),
    Num(f64),
    Str(String),
    Arr(Vec<Json>),
    /// Fields in document order. Keys may repeat; the first one wins.
    Obj(Vec<(String, Json)>),
}

/// The value at a dotted `path` such as `"users.0.name"`, or `None`. The empty path is `root` itself.
pub fn get<'a>(root: &'a Json, path: &str) -> Option<&'a Json> {
    if path.is_empty() {
        return Some(root);
    }
    let mut node = root;
    for seg in path.split('.') {
        node = match node {
            Json::Obj(fields) => &fields.iter().find(|(k, _)| k == seg)?.1,
            Json::Arr(items) => {
                if seg.is_empty() || !seg.bytes().all(|b| b.is_ascii_digit()) {
                    return None;
                }
                items.get(seg.parse::<usize>().ok()?)?
            }
            _ => return None,
        };
    }
    Some(node)
}

/// The number at `path`, if there is a number there.
pub fn num_at(root: &Json, path: &str) -> Option<f64> {
    let Json::Num(n) = get(root, path)? else {
        return None;
    };
    Some(*n)
}

/// True if `path` exists and holds `null`.
pub fn is_null_at(root: &Json, path: &str) -> bool {
    get(root, path).is_none_or(|v| matches!(v, Json::Null))
}
