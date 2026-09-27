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
fn record_after_a_tie() {
    check!(r#"record (4, "a"), (4, "b"), (6, "c")"#, run(&[(4, "a"), (4, "b"), (6, "c")]), ("c".to_string(), Some(2)));
}

#[test]
fn same_label_twice() {
    check!(r#"record (1, "x"), (3, "x"), (2, "y")"#, run(&[(1, "x"), (3, "x"), (2, "y")]), ("x".to_string(), None));
}

#[test]
fn empty_label() {
    check!(r#"record (1, ""), (0, "z")"#, run(&[(1, ""), (0, "z")]), ("".to_string(), None));
}

#[test]
fn chain_of_records() {
    check!(r#"record (1, "a"), (2, "b"), (4, "c"), (8, "d")"#, run(&[(1, "a"), (2, "b"), (4, "c"), (8, "d")]), ("d".to_string(), Some(4)));
}

#[test]
fn far_apart() {
    check!(r#"record (-1000000000000, "lo"), (1000000000000, "hi")"#, run(&[(-1000000000000, "lo"), (1000000000000, "hi")]), ("hi".to_string(), Some(2000000000000)));
}

#[test]
fn all_equal() {
    check!(r#"record (0, "p"), (0, "q"), (0, "r")"#, run(&[(0, "p"), (0, "q"), (0, "r")]), ("p".to_string(), None));
}

#[test]
fn unicode_labels() {
    check!(r#"record (2, "é"), (7, "日本")"#, run(&[(2, "é"), (7, "日本")]), ("日本".to_string(), Some(5)));
}

#[test]
fn holder_is_the_stored_label() {
    let mut s = Series::new();
    let seven = "seven".to_string();
    let moved = seven.as_ptr();
    s.record(7, seven);
    check!("record (7, \"seven\"): the label String is moved in, not copied", s.labels[0].as_ptr() == moved, true);
    let p = s.record(3, "three".to_string()).0.as_ptr();
    check!("then (3, \"three\"): the returned &str is labels[0] itself", p == s.labels[0].as_ptr(), true);
    let p = s.record(8, "eight".to_string()).0.as_ptr();
    check!("then (8, \"eight\"): the returned &str is labels[2] itself", p == s.labels[2].as_ptr(), true);
    check!("points afterwards", s.points.clone(), vec![7, 3, 8]);
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6201);
    for _ in 0..300 {
        let n = 1 + rng.below(8);
        let mut s = Series::new();
        let (mut pts, mut labs): (Vec<i64>, Vec<String>) = (Vec::new(), Vec::new());
        let mut log = Vec::new();
        for i in 0..n {
            let x = rng.int(-4, 4);
            let l = format!("{}{i}", rng.string(1, "ab"));
            log.push(format!("({x}, {l:?})"));
            let want = match pts.iter().copied().max() {
                Some(b) if x <= b => (labs[pts.iter().position(|&p| p == b).unwrap()].clone(), None),
                Some(b) => (l.clone(), Some(x - b)),
                None => (l.clone(), None),
            };
            pts.push(x);
            labs.push(l.clone());
            let (h, g) = s.record(x, l);
            check!(format!("record {}", log.join(", ")), (h.to_string(), g), want);
        }
    }
}
