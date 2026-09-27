use std::collections::HashMap;

pub fn find_itinerary(tickets: &[(&str, &str)]) -> Vec<String> {
    // Intern airports so the graph is plain indices.
    let mut id: HashMap<&str, usize> = HashMap::from([("JFK", 0)]);
    let mut name = vec!["JFK"];
    let mut out: Vec<Vec<usize>> = vec![Vec::new()];
    for &(from, to) in tickets {
        for airport in [from, to] {
            id.entry(airport).or_insert_with(|| {
                name.push(airport);
                out.push(Vec::new());
                name.len() - 1
            });
        }
        out[id[from]].push(id[to]);
    }
    // Largest first, so `pop` hands out the smallest.
    for next in &mut out {
        next.sort_unstable_by(|&a, &b| name[b].cmp(name[a]));
    }

    // Hierholzer: walk until stuck, then that airport is finished; finished airports come out in reverse.
    let mut stack = vec![0];
    let mut route = Vec::with_capacity(tickets.len() + 1);
    while let Some(&u) = stack.last() {
        match out[u].pop() {
            Some(v) => stack.push(v),
            None => route.push(stack.pop().expect("stack is not empty")),
        }
    }
    route.iter().rev().map(|&u| name[u].to_string()).collect()
}
