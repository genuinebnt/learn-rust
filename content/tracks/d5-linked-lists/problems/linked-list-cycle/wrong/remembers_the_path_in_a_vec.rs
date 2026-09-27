/// Where the list starting at `head` enters a cycle, if it has one.
pub fn cycle_start(next: &[Option<usize>], head: Option<usize>) -> Option<usize> {
    let mut path: Vec<usize> = Vec::new();
    let mut cur = head;
    while let Some(i) = cur {
        if path.contains(&i) {
            return Some(i);
        }
        path.push(i);
        cur = next[i];
    }
    None
}

pub fn has_cycle(next: &[Option<usize>], head: Option<usize>) -> bool {
    cycle_start(next, head).is_some()
}
