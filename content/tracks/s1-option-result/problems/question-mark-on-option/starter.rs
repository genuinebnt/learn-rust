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
    todo!()
}

/// The number at `path`, if there is a number there.
pub fn num_at(root: &Json, path: &str) -> Option<f64> {
    todo!()
}

/// True if `path` exists and holds `null`.
pub fn is_null_at(root: &Json, path: &str) -> bool {
    todo!()
}
