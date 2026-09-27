use std::collections::BTreeMap;

pub fn between(events: &BTreeMap<u32, String>, from: u32, to: u32) -> Vec<&str> {
    events.range(from..=to).map(|(_, name)| name.as_str()).collect()
}
