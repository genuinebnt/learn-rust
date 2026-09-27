use std::collections::HashMap;

pub fn find_itinerary(tickets: &[(&str, &str)]) -> Vec<String> {
    let mut out: HashMap<&str, Vec<&str>> = HashMap::new();
    for &(from, to) in tickets {
        out.entry(from).or_default().push(to);
    }
    for next in out.values_mut() {
        next.sort_unstable();
    }
    let mut stack = vec!["JFK"];
    let mut route = Vec::new();
    while let Some(&u) = stack.last() {
        match out.get_mut(u).and_then(|n| n.pop()) {
            Some(v) => stack.push(v),
            None => route.push(stack.pop().unwrap()),
        }
    }
    route.iter().rev().map(|s| s.to_string()).collect()
}
