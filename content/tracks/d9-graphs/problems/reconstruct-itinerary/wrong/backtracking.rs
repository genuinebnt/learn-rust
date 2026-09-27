use std::collections::HashMap;

fn search<'a>(at: &'a str, out: &HashMap<&'a str, Vec<(&'a str, usize)>>, used: &mut [bool], path: &mut Vec<&'a str>, total: usize) -> bool {
    if path.len() == total + 1 {
        return true;
    }
    if let Some(next) = out.get(at) {
        for &(to, id) in next {
            if used[id] {
                continue;
            }
            used[id] = true;
            path.push(to);
            if search(to, out, used, path, total) {
                return true;
            }
            path.pop();
            used[id] = false;
        }
    }
    false
}

pub fn find_itinerary(tickets: &[(&str, &str)]) -> Vec<String> {
    let mut out: HashMap<&str, Vec<(&str, usize)>> = HashMap::new();
    for (id, &(from, to)) in tickets.iter().enumerate() {
        out.entry(from).or_default().push((to, id));
    }
    for next in out.values_mut() {
        next.sort_unstable();
    }
    let mut path = vec!["JFK"];
    search("JFK", &out, &mut vec![false; tickets.len()], &mut path, tickets.len());
    path.into_iter().map(String::from).collect()
}
