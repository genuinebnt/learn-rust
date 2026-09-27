use solution::*;

#[test]
fn four_cities() {
    check!(r#"n = 4, roads = [(0,1,3), (1,2,1), (1,3,4), (2,3,1)], threshold = 4"#, find_the_city(4, &[(0, 1, 3), (1, 2, 1), (1, 3, 4), (2, 3, 1)], 4), 3);
}

#[test]
fn five_cities() {
    check!(r#"n = 5, roads = [(0,1,2), (0,4,8), (1,2,3), (1,4,2), (2,3,1), (3,4,1)], threshold = 2"#, find_the_city(5, &[(0, 1, 2), (0, 4, 8), (1, 2, 3), (1, 4, 2), (2, 3, 1), (3, 4, 1)], 2), 0);
}

#[test]
fn no_roads_tie_goes_to_the_largest() {
    check!(r#"n = 2, roads = [], threshold = 5"#, find_the_city(2, &[], 5), 1);
}

#[test]
fn shortest_route_not_fewest_roads() {
    check!(r#"n = 3, roads = [(0,1,10), (0,2,1), (2,1,1)], threshold = 2"#, find_the_city(3, &[(0, 1, 10), (0, 2, 1), (2, 1, 1)], 2), 2);
}

#[test]
fn end_of_a_line() {
    check!(r#"n = 4, path 0-1-2-3 of length 1 each, threshold = 1"#, find_the_city(4, &[(0, 1, 1), (1, 2, 1), (2, 3, 1)], 1), 3);
}
