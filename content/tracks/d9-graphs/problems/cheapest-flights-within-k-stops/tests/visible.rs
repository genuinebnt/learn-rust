use solution::*;

#[test]
fn one_stop() {
    check!(r#"n = 3, flights = [(0,1,100), (1,2,100), (0,2,500)], src = 0, dst = 2, k = 1"#, find_cheapest_price(3, &[(0, 1, 100), (1, 2, 100), (0, 2, 500)], 0, 2, 1), Some(200));
}

#[test]
fn no_stops() {
    check!(r#"same flights, k = 0"#, find_cheapest_price(3, &[(0, 1, 100), (1, 2, 100), (0, 2, 500)], 0, 2, 0), Some(500));
}

#[test]
fn cheaper_route_needs_too_many_stops() {
    check!(r#"n = 4, flights = [(0,1,100),(1,2,100),(2,0,100),(1,3,600),(2,3,200)], src = 0, dst = 3, k = 1"#, find_cheapest_price(4, &[(0, 1, 100), (1, 2, 100), (2, 0, 100), (1, 3, 600), (2, 3, 200)], 0, 3, 1), Some(700));
}

#[test]
fn no_route() {
    check!(r#"n = 3, flights = [(1,2,5)], src = 0, dst = 2, k = 2"#, find_cheapest_price(3, &[(1, 2, 5)], 0, 2, 2), None);
}

#[test]
fn already_there() {
    check!(r#"n = 2, flights = [(0,1,5)], src = 1, dst = 1, k = 0"#, find_cheapest_price(2, &[(0, 1, 5)], 1, 1, 0), Some(0));
}
