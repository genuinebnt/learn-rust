use std::collections::HashMap;

pub fn get_or_create<'m>(map: &'m mut HashMap<String, Vec<u32>>, key: &str) -> &'m mut Vec<u32> {
    map.entry(key.to_string()).or_default()
}
