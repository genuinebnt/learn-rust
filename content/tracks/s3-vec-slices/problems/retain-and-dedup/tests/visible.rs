use solution::*;

#[test]
fn tick_decrements_and_drops() {
    let mut j = vec![Job { id: 1, retries_left: 2 }, Job { id: 2, retries_left: 1 }, Job { id: 3, retries_left: 5 }];
    tick(&mut j);
    check!(r#"jobs (id, retries_left) = [(1, 2), (2, 1), (3, 5)]"#, j, vec![Job { id: 1, retries_left: 1 }, Job { id: 3, retries_left: 4 }]);
}

#[test]
fn merge_neighbours() {
    let mut r = vec![Run { key: 'a', count: 2 }, Run { key: 'a', count: 3 }, Run { key: 'b', count: 1 }, Run { key: 'a', count: 1 }];
    merge_runs(&mut r);
    check!(r#"runs = [(a, 2), (a, 3), (b, 1), (a, 1)]"#, r, vec![Run { key: 'a', count: 5 }, Run { key: 'b', count: 1 }, Run { key: 'a', count: 1 }]);
}

#[test]
fn first_of_each_minute() {
    let mut e = vec![(0, "a".to_string()), (59, "b".to_string()), (60, "c".to_string()), (61, "d".to_string())];
    first_per_minute(&mut e);
    check!(r#"events = [(0, "a"), (59, "b"), (60, "c"), (61, "d")]"#, e, vec![(0, "a".to_string()), (60, "c".to_string())]);
}

#[test]
fn tick_empty() {
    let mut j = Vec::<Job>::new();
    tick(&mut j);
    check!(r#"jobs (id, retries_left) = []"#, j, Vec::<Job>::new());
}

#[test]
fn merge_nothing_to_merge() {
    let mut r = vec![Run { key: 'a', count: 1 }, Run { key: 'b', count: 2 }];
    merge_runs(&mut r);
    check!(r#"runs = [(a, 1), (b, 2)]"#, r, vec![Run { key: 'a', count: 1 }, Run { key: 'b', count: 2 }]);
}
