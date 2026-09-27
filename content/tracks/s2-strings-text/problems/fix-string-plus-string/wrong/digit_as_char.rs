/// "last, first"
pub fn full_name(first: String, last: String) -> String {
    last + ", " + &first
}

/// "name#id"
pub fn tag(name: &str, id: u32) -> String {
    name.to_string() + "#" + &((b'0' + id as u8) as char).to_string()
}
