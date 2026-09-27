#[derive(Debug, PartialEq)]
pub struct Tag {
    pub name: String,
}

impl Tag {
    pub fn new(name: &str) -> Tag {
        Tag { name: String::with_capacity(name.len()) }
    }
}
