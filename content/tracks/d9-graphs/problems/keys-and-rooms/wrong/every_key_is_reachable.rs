pub fn can_visit_all_rooms(rooms: &[Vec<usize>]) -> bool {
    // Wrong: checks that a key to every room exists somewhere, not that you can reach it.
    let mut has_key = vec![false; rooms.len()];
    has_key[0] = true;
    for keys in rooms {
        for &k in keys {
            has_key[k] = true;
        }
    }
    has_key.iter().all(|&h| h)
}
