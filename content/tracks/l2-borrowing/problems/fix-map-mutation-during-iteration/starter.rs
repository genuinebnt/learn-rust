use std::collections::HashMap;

#[derive(Debug, PartialEq)]
pub struct Session {
    pub parent: Option<u32>,
    pub expires: u64,
    pub bytes: u64,
}

/// Removes every session that has expired (`expires <= now`). Each removed session's bytes are credited to
/// its parent, if the parent is still there after this call; credit isn't passed further up. Returns the
/// removed ids, sorted.
pub fn expire(sessions: &mut HashMap<u32, Session>, now: u64) -> Vec<u32> {
    let mut removed = Vec::new();
    for (id, s) in sessions.iter() {
        if s.expires <= now {
            if let Some(p) = s.parent {
                if let Some(parent) = sessions.get_mut(&p) {
                    parent.bytes += s.bytes;
                }
            }
            sessions.remove(id);
            removed.push(*id);
        }
    }
    removed.sort();
    removed
}
