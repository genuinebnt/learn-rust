/// "last, first"
pub fn full_name(first: String, last: String) -> String {
    first + ", " + &last
}

/// "name#id"
pub fn tag(name: &str, id: u32) -> String {
    format!("{name}#{id}")
}
