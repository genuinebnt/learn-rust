/// Where the list starting at `head` enters a cycle, if it has one.
pub fn cycle_start(next: &[Option<usize>], head: Option<usize>) -> Option<usize> {
    todo!()
}

pub fn has_cycle(next: &[Option<usize>], head: Option<usize>) -> bool {
    cycle_start(next, head).is_some()
}
