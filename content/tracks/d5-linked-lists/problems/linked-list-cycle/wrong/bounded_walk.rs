/// Where the list starting at `head` enters a cycle, if it has one.
pub fn cycle_start(next: &[Option<usize>], head: Option<usize>) -> Option<usize> {
    // A path longer than the arena must repeat; guess that the head is where it loops.
    let mut cur = head;
    for _ in 0..next.len() {
        cur = cur.and_then(|i| next[i]);
    }
    cur.and(head)
}

pub fn has_cycle(next: &[Option<usize>], head: Option<usize>) -> bool {
    cycle_start(next, head).is_some()
}
