use std::cmp::Reverse;

pub fn reconstruct_queue(people: &[(u32, usize)]) -> Vec<(u32, usize)> {
    let mut sorted = people.to_vec();
    // Tallest first; among equal heights, the one with fewer people in front first.
    sorted.sort_unstable_by_key(|&(h, k)| (Reverse(h), k));
    let mut queue = Vec::with_capacity(sorted.len());
    for person in sorted {
        // Everyone placed so far is at least as tall, so index k is exactly right.
        queue.insert(person.1, person);
    }
    queue
}
