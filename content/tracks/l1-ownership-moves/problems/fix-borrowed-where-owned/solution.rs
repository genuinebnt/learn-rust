#[derive(Debug, PartialEq)]
pub struct Tag {
    pub name: String,
}

impl Tag {
    pub fn new(name: &str) -> Tag {
        Tag { name: name.to_string() }
    }
}
