use std::collections::HashMap;

#[derive(Debug, PartialEq)]
pub struct Session {
    pub parent: Option<u32>,
    pub expires: u64,
    pub bytes: u64,
}

pub fn expire(sessions: &mut HashMap<u32, Session>, now: u64) -> Vec<u32> {
    let mut ids: Vec<u32> = sessions.iter().filter(|(_, s)| s.expires <= now).map(|(&id, _)| id).collect();
    ids.sort_unstable();
    for &id in &ids {
        let s = sessions.remove(&id).unwrap();
        if let Some(parent) = s.parent.and_then(|p| sessions.get_mut(&p)) {
            parent.bytes += s.bytes;
        }
    }
    ids
}
