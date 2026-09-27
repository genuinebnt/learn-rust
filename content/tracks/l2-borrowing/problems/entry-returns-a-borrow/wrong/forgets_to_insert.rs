use std::collections::HashMap;

pub fn get_or_create<'m>(map: &'m mut HashMap<String, Vec<u32>>, key: &str) -> &'m mut Vec<u32> {
    if !map.contains_key(key) {
        return Box::leak(Box::new(Vec::new()));
    }
    map.get_mut(key).unwrap()
}
