pub fn can_visit_all_rooms(rooms: &[Vec<usize>]) -> bool {
    let mut visited = vec![0];
    let mut i = 0;
    while i < visited.len() {
        let room = visited[i];
        i += 1;
        for &key in &rooms[room] {
            if !visited.contains(&key) {
                visited.push(key);
            }
        }
    }
    visited.len() == rooms.len()
}
