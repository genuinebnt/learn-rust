/// "last, first"
pub fn full_name(first: String, last: String) -> String {
    last + ", " + first
}

/// "name#id"
pub fn tag(name: &str, id: u32) -> String {
    name + "#" + id
}
