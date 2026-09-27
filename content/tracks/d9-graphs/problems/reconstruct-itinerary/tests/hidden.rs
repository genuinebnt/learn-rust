use solution::*;

#[test]
fn single_ticket() {
    check!(r#"tickets = [("JFK","LAX")]"#, find_itinerary(&[("JFK", "LAX")]), vec!["JFK", "LAX"]);
}

#[test]
fn self_loop_first() {
    check!(r#"tickets = [("JFK","AAA"), ("JFK","JFK")]"#, find_itinerary(&[("JFK", "AAA"), ("JFK", "JFK")]), vec!["JFK", "JFK", "AAA"]);
}

#[test]
fn dead_end_deeper_down() {
    check!(r#"tickets = [("JFK","AAA"), ("AAA","BBB"), ("AAA","CCC"), ("CCC","AAA")]"#, find_itinerary(&[("JFK", "AAA"), ("AAA", "BBB"), ("AAA", "CCC"), ("CCC", "AAA")]), vec!["JFK", "AAA", "CCC", "AAA", "BBB"]);
}

#[test]
fn two_detours() {
    check!(r#"tickets = [("JFK","AAA"), ("JFK","BBB"), ("BBB","JFK"), ("JFK","CCC"), ("CCC","JFK")]"#, find_itinerary(&[("JFK", "AAA"), ("JFK", "BBB"), ("BBB", "JFK"), ("JFK", "CCC"), ("CCC", "JFK")]), vec!["JFK", "BBB", "JFK", "CCC", "JFK", "AAA"]);
}

#[test]
fn ends_back_home() {
    check!(r#"tickets = [("JFK","SFO"), ("SFO","ATL"), ("ATL","JFK")]"#, find_itinerary(&[("JFK", "SFO"), ("SFO", "ATL"), ("ATL", "JFK")]), vec!["JFK", "SFO", "ATL", "JFK"]);
}

#[test]
fn never_back_to_start() {
    check!(r#"tickets = [("JFK","ZZZ"), ("ZZZ","AAA"), ("AAA","ZZZ"), ("ZZZ","BBB")]"#, find_itinerary(&[("JFK", "ZZZ"), ("ZZZ", "AAA"), ("AAA", "ZZZ"), ("ZZZ", "BBB")]), vec!["JFK", "ZZZ", "AAA", "ZZZ", "BBB"]);
}

#[test]
fn leetcode_tricky() {
    check!(r#"tickets = [("EZE","AXA"), ("TIA","ANU"), ("ANU","JFK"), ("JFK","ANU"), ("ANU","EZE"), ("TIA","ANU"), ("AXA","TIA"), ("TIA","JFK"), ("ANU","TIA"), ("JFK","TIA")]"#, find_itinerary(&[("EZE", "AXA"), ("TIA", "ANU"), ("ANU", "JFK"), ("JFK", "ANU"), ("ANU", "EZE"), ("TIA", "ANU"), ("AXA", "TIA"), ("TIA", "JFK"), ("ANU", "TIA"), ("JFK", "TIA")]), vec!["JFK", "ANU", "EZE", "AXA", "TIA", "ANU", "JFK", "TIA", "ANU", "TIA", "JFK"]);
}

#[test]
fn random_vs_brute_force() {
    // Brute force: depth-first over tickets in sorted order; the first full itinerary is the smallest.
    fn search<'a>(at: &'a str, tickets: &[(&'a str, &'a str)], used: &mut Vec<bool>, path: &mut Vec<&'a str>) -> bool {
        if path.len() == tickets.len() + 1 {
            return true;
        }
        let mut options: Vec<usize> = (0..tickets.len()).filter(|&i| !used[i] && tickets[i].0 == at).collect();
        options.sort_by_key(|&i| tickets[i].1);
        for i in options {
            used[i] = true;
            path.push(tickets[i].1);
            if search(tickets[i].1, tickets, used, path) {
                return true;
            }
            path.pop();
            used[i] = false;
        }
        false
    }

    let mut rng = anneal_prelude::Rng::new(957);
    let airports = ["JFK", "ATL", "SFO", "LHR"];
    for _ in 0..300 {
        // A random walk from JFK, shuffled, is always a valid ticket set.
        let len = rng.below(9);
        let mut at = "JFK";
        let mut tickets: Vec<(&str, &str)> = Vec::new();
        for _ in 0..len {
            let to = *rng.pick(&airports);
            tickets.push((at, to));
            at = to;
        }
        rng.shuffle(&mut tickets);
        let mut path = vec!["JFK"];
        search("JFK", &tickets, &mut vec![false; tickets.len()], &mut path);
        let want: Vec<String> = path.iter().map(|s| s.to_string()).collect();
        check!(format!("tickets = {tickets:?}"), find_itinerary(&tickets), want);
    }
}

fn big_stack<R: Send + 'static>(f: impl FnOnce() -> R + Send + 'static) -> R {
    std::thread::Builder::new().stack_size(512 << 20).spawn(f).unwrap().join().unwrap()
}

#[test]
fn scale_dead_end_tried_first() {
    // JFK has 50000 round trips to B00000..B49999 and one ticket to AAAAAA, which starts a
    // 100000-ticket path that never returns. AAAAAA is the smallest choice every time but must come last.
    let got = big_stack(|| {
        let k = 50_000;
        let l = 100_000;
        let names: Vec<String> = (0..k).map(|i| format!("B{i:05}")).chain((1..=l).map(|i| format!("P{i:05}"))).collect();
        let mut tickets: Vec<(&str, &str)> = Vec::new();
        for b in &names[..k] {
            tickets.push(("JFK", b.as_str()));
            tickets.push((b.as_str(), "JFK"));
        }
        tickets.push(("JFK", "AAAAAA"));
        tickets.push(("AAAAAA", names[k].as_str()));
        for i in k..k + l - 1 {
            tickets.push((names[i].as_str(), names[i + 1].as_str()));
        }
        let out = find_itinerary(&tickets);
        (out.len(), out[1].clone(), out[2 * k].clone(), out[2 * k + 1].clone(), out[out.len() - 1].clone())
    });
    check!("50000 round trips from JFK, then a 100001-ticket one-way chain",
           got, (200_002, "B00000".to_string(), "JFK".to_string(), "AAAAAA".to_string(), "P100000".to_string()));
}
