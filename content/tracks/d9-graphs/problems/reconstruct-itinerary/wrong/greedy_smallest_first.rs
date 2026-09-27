use std::collections::HashMap;

pub fn find_itinerary(tickets: &[(&str, &str)]) -> Vec<String> {
    let mut out: HashMap<&str, Vec<&str>> = HashMap::new();
    for &(from, to) in tickets {
        out.entry(from).or_default().push(to);
    }
    for next in out.values_mut() {
        next.sort_unstable_by(|a, b| b.cmp(a));
    }
    let mut route = vec!["JFK".to_string()];
    let mut at = "JFK";
    while let Some(next) = out.get_mut(at).and_then(|n| n.pop()) {
        route.push(next.to_string());
        at = next;
    }
    route
}
