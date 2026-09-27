pub fn can_visit_all_rooms(rooms: &[Vec<usize>]) -> bool {
    fn enter(room: usize, rooms: &[Vec<usize>], seen: &mut [bool]) {
        seen[room] = true;
        for &key in &rooms[room] {
            if !seen[key] {
                enter(key, rooms, seen);
            }
        }
    }
    let mut seen = vec![false; rooms.len()];
    enter(0, rooms, &mut seen);
    seen.iter().all(|&s| s)
}
