use solution::*;

#[test]
fn one_way_through() {
    check!(r#"tickets = [("MUC","LHR"), ("JFK","MUC"), ("SFO","SJC"), ("LHR","SFO")]"#, find_itinerary(&[("MUC", "LHR"), ("JFK", "MUC"), ("SFO", "SJC"), ("LHR", "SFO")]), vec!["JFK", "MUC", "LHR", "SFO", "SJC"]);
}

#[test]
fn smallest_of_several() {
    check!(r#"tickets = [("JFK","SFO"), ("JFK","ATL"), ("SFO","ATL"), ("ATL","JFK"), ("ATL","SFO")]"#, find_itinerary(&[("JFK", "SFO"), ("JFK", "ATL"), ("SFO", "ATL"), ("ATL", "JFK"), ("ATL", "SFO")]), vec!["JFK", "ATL", "JFK", "SFO", "ATL", "SFO"]);
}

#[test]
fn no_tickets() {
    check!(r#"tickets = []"#, find_itinerary(&[]), vec!["JFK"]);
}

#[test]
fn smallest_is_a_dead_end() {
    check!(r#"tickets = [("JFK","KUL"), ("JFK","NRT"), ("NRT","JFK")]"#, find_itinerary(&[("JFK", "KUL"), ("JFK", "NRT"), ("NRT", "JFK")]), vec!["JFK", "NRT", "JFK", "KUL"]);
}

#[test]
fn repeated_ticket() {
    check!(r#"tickets = [("JFK","ATL"), ("ATL","JFK"), ("JFK","ATL"), ("ATL","JFK")]"#, find_itinerary(&[("JFK", "ATL"), ("ATL", "JFK"), ("JFK", "ATL"), ("ATL", "JFK")]), vec!["JFK", "ATL", "JFK", "ATL", "JFK"]);
}
