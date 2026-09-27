use std::collections::HashMap;

pub fn get_or_create<'m>(map: &'m mut HashMap<String, Vec<u32>>, key: &str) -> &'m mut Vec<u32> {
    map.insert(key.to_string(), Vec::new());
    map.get_mut(key).unwrap()
}
