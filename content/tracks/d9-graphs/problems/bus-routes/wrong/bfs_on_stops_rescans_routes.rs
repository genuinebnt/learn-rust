use std::collections::{HashMap, HashSet, VecDeque};

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
    let mut seen = HashSet::from([source]);
    let mut queue = VecDeque::from([(source, 0)]);
    while let Some((stop, count)) = queue.pop_front() {
        for &bus in buses_at.get(&stop).into_iter().flatten() {
            for &next in &routes[bus] {
                if next == target {
                    return Some(count + 1);
                }
                if seen.insert(next) {
                    queue.push_back((next, count + 1));
                }
            }
        }
    }
    None
}
