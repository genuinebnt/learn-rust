use solution::*;

/// Records every (x, label) in order and returns the last result, owned.
fn run(points: &[(i64, &str)]) -> (String, Option<i64>) {
    let mut s = Series::new();
    let mut last = (String::new(), None);
    for &(x, l) in points {
        let (h, g) = s.record(x, l.to_string());
        last = (h.to_string(), g);
    }
    last
}

#[test]
fn first_point() {
    check!(r#"record (5, "a")"#, run(&[(5, "a")]), ("a".to_string(), None));
}

#[test]
fn new_record() {
    check!(r#"record (5, "a"), (9, "b")"#, run(&[(5, "a"), (9, "b")]), ("b".to_string(), Some(4)));
}

#[test]
fn below_the_record() {
    check!(r#"record (5, "a"), (3, "b")"#, run(&[(5, "a"), (3, "b")]), ("a".to_string(), None));
}

#[test]
fn tie_keeps_the_holder() {
    check!(r#"record (5, "a"), (5, "b")"#, run(&[(5, "a"), (5, "b")]), ("a".to_string(), None));
}

#[test]
fn first_to_reach_the_max() {
    check!(r#"record (5, "a"), (9, "b"), (9, "c"), (2, "d")"#, run(&[(5, "a"), (9, "b"), (9, "c"), (2, "d")]), ("b".to_string(), None));
}

#[test]
fn negatives() {
    check!(r#"record (-5, "a"), (-2, "b")"#, run(&[(-5, "a"), (-2, "b")]), ("b".to_string(), Some(3)));
}
