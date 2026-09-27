fn step(next: &[Option<usize>], i: Option<usize>) -> Option<usize> {
    i.and_then(|i| next[i])
}

/// Where the list starting at `head` enters a cycle, if it has one.
pub fn cycle_start(next: &[Option<usize>], head: Option<usize>) -> Option<usize> {
    let (mut slow, mut fast) = (head, head);
    loop {
        slow = step(next, slow);
        fast = step(next, step(next, fast));
        match (slow, fast) {
            (Some(s), Some(f)) if s == f => return Some(s),
            (_, None) => return None,
            _ => {}
        }
    }
}

pub fn has_cycle(next: &[Option<usize>], head: Option<usize>) -> bool {
    cycle_start(next, head).is_some()
}
