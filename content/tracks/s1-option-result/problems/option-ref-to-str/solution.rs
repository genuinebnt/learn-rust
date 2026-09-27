use std::collections::HashMap;

pub fn label(labels: &HashMap<u32, String>, id: u32) -> Option<&str> {
    labels.get(&id).map(String::as_str)
}

pub fn label_or<'a>(labels: &'a HashMap<u32, String>, id: u32, default: &'a str) -> &'a str {
    label(labels, id).unwrap_or(default)
}
