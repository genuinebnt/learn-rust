use solution::*;

#[test]
fn snapshot_matters() {
    check!(r#"n = 4, flights = [(0,1,100),(1,2,100),(2,0,100),(1,3,600),(2,3,200)], src = 0, dst = 3, k = 1"#, find_cheapest_price(4, &[(0, 1, 100), (1, 2, 100), (2, 0, 100), (1, 3, 600), (2, 3, 200)], 0, 3, 1), Some(700));
}

#[test]
fn chain_order() {
    check!(r#"flights listed so one round could chain them: [(0,1,1), (1,2,1)], k = 0"#, find_cheapest_price(3, &[(0, 1, 1), (1, 2, 1)], 0, 2, 0), None);
}

#[test]
fn unreachable() {
    check!(r#"n = 2, flights = [], src = 0, dst = 1, k = 1"#, find_cheapest_price(2, &[], 0, 1, 1), None);
}
