pub fn reconstruct_queue(people: &[(u32, usize)]) -> Vec<(u32, usize)> {
    let mut sorted = people.to_vec();
    sorted.sort_unstable();
    let mut queue = Vec::new();
    for person in sorted {
        queue.insert(person.1.min(queue.len()), person);
    }
    queue
}
