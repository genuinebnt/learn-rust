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
    let gone: Vec<(u32, Session)> = sessions.extract_if(|_, s| s.expires <= now).collect();
    let mut removed = Vec::with_capacity(gone.len());
    for (id, s) in gone {
        if let Some(parent) = s.parent.and_then(|p| sessions.get_mut(&p)) {
            parent.bytes = parent.bytes.max(s.bytes);
        }
        removed.push(id);
    }
    removed.sort_unstable();
    removed
}
