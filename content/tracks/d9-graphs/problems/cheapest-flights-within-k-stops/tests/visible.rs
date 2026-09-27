use solution::*;

#[test]
fn one_stop() {
    check!(r#"n = 3, flights = [(0,1,100), (1,2,100), (0,2,500)], src = 0, dst = 2, k = 1"#, find_cheapest_price(3, &[(0, 1, 100), (1, 2, 100), (0, 2, 500)], 0, 2, 1), Some(200));
}

#[test]
fn no_stops() {
    check!(r#"same flights, k = 0"#, find_cheapest_price(3, &[(0, 1, 100), (1, 2, 100), (0, 2, 500)], 0, 2, 0), Some(500));
}
