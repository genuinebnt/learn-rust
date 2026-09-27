pub fn can_visit_all_rooms(rooms: &[Vec<usize>]) -> bool {
    let mut seen = vec![false; rooms.len()];
    seen[0] = true;
    let mut entered = 1;
    let mut stack = vec![0];
    while let Some(room) = stack.pop() {
        for &key in &rooms[room] {
            if !seen[key] {
                seen[key] = true;
                entered += 1;
                stack.push(key);
            }
        }
    }
    entered == rooms.len()
}
