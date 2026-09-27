use solution::*;

#[test]
fn change_once() {
    check!(r#"routes = [[1,2,7], [3,6,7]], source = 1, target = 6"#, num_buses_to_destination(&[vec![1, 2, 7], vec![3, 6, 7]], 1, 6), Some(2));
}

#[test]
fn unreachable() {
    check!(r#"routes = [[7,12], [4,5,15], [6], [15,19], [9,12,13]], source = 15, target = 12"#, num_buses_to_destination(&[vec![7, 12], vec![4, 5, 15], vec![6], vec![15, 19], vec![9, 12, 13]], 15, 12), None);
}

#[test]
fn already_there() {
    check!(r#"routes = [[1,2]], source = 2, target = 2"#, num_buses_to_destination(&[vec![1, 2]], 2, 2), Some(0));
}

#[test]
fn count_buses_not_stops() {
    check!(r#"routes = [[1,2,3,4,5]], source = 1, target = 5"#, num_buses_to_destination(&[vec![1, 2, 3, 4, 5]], 1, 5), Some(1));
}

#[test]
fn routes_loop() {
    check!(r#"routes = [[5,1,9]], source = 9, target = 5"#, num_buses_to_destination(&[vec![5, 1, 9]], 9, 5), Some(1));
}
