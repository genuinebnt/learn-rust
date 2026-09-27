pub fn reconstruct_queue(people: &[(u32, usize)]) -> Vec<(u32, usize)> {
    // Front to back: the next person is the shortest whose k matches who's already placed.
    let mut left = people.to_vec();
    let mut queue: Vec<(u32, usize)> = Vec::new();
    while !left.is_empty() {
        let mut pick: Option<usize> = None;
        for (i, &(h, k)) in left.iter().enumerate() {
            let taller = queue.iter().filter(|q| q.0 >= h).count();
            if taller == k && pick.map_or(true, |j| h < left[j].0) {
                pick = Some(i);
            }
        }
        queue.push(left.remove(pick.unwrap()));
    }
    queue
}
