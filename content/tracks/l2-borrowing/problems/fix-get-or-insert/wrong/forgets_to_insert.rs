use std::collections::HashMap;

/// The value for `key`, inserting `default` first if it's missing.
pub fn get_or_insert<'m>(map: &'m mut HashMap<u32, String>, key: u32, default: &str) -> &'m String {
    if !map.contains_key(&key) {
        return Box::leak(Box::new(default.to_string()));
    }
    &map[&key]
}
