use std::collections::{HashMap, VecDeque};

pub fn num_buses_to_destination(routes: &[Vec<u32>], source: u32, target: u32) -> Option<u32> {
    if source == target {
        return Some(0);
    }
    let mut buses_at: HashMap<u32, Vec<usize>> = HashMap::new();
    for (bus, route) in routes.iter().enumerate() {
        for &stop in route {
            buses_at.entry(stop).or_default().push(bus);
        }
    }
    let mut taken = vec![false; routes.len()];
    let mut queue = VecDeque::new();
    for &bus in buses_at.get(&source).into_iter().flatten() {
        if !taken[bus] {
            taken[bus] = true;
            queue.push_back((bus, 0));
        }
    }
    while let Some((bus, changes)) = queue.pop_front() {
        if routes[bus].contains(&target) {
            return Some(changes);
        }
        for stop in &routes[bus] {
            for next in buses_at.remove(stop).into_iter().flatten() {
                if !taken[next] {
                    taken[next] = true;
                    queue.push_back((next, changes + 1));
                }
            }
        }
    }
    None
}
