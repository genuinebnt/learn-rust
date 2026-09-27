use solution::*;

#[test]
fn center_in_the_middle() {
    check!(r#"edges = [(1, 2), (2, 3), (4, 2)]"#, find_center(&[(1, 2), (2, 3), (4, 2)]), 2);
}

#[test]
fn center_first() {
    check!(r#"edges = [(1, 2), (5, 1), (1, 3), (1, 4)]"#, find_center(&[(1, 2), (5, 1), (1, 3), (1, 4)]), 1);
}

#[test]
fn smallest_star() {
    check!(r#"edges = [(3, 1), (1, 2)]"#, find_center(&[(3, 1), (1, 2)]), 1);
}

#[test]
fn center_always_second() {
    check!(r#"edges = [(2, 9), (3, 9), (4, 9)]"#, find_center(&[(2, 9), (3, 9), (4, 9)]), 9);
}

#[test]
fn center_not_the_smallest_label() {
    check!(r#"edges = [(7, 100), (100, 1)]"#, find_center(&[(7, 100), (100, 1)]), 100);
}
