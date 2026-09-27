use solution::*;

#[test]
fn tick_zero_is_removed() {
    let mut j = vec![Job { id: 1, retries_left: 0 }, Job { id: 2, retries_left: 3 }];
    tick(&mut j);
    check!(r#"jobs (id, retries_left) = [(1, 0), (2, 3)]"#, j, vec![Job { id: 2, retries_left: 2 }]);
}

#[test]
fn tick_all_expire() {
    let mut j = vec![Job { id: 1, retries_left: 1 }, Job { id: 2, retries_left: 1 }];
    tick(&mut j);
    check!(r#"jobs (id, retries_left) = [(1, 1), (2, 1)]"#, j, Vec::<Job>::new());
}

#[test]
fn tick_keeps_order() {
    let mut j = vec![Job { id: 5, retries_left: 9 }, Job { id: 3, retries_left: 1 }, Job { id: 4, retries_left: 2 }, Job { id: 1, retries_left: 7 }];
    tick(&mut j);
    check!(r#"jobs (id, retries_left) = [(5, 9), (3, 1), (4, 2), (1, 7)]"#, j, vec![Job { id: 5, retries_left: 8 }, Job { id: 4, retries_left: 1 }, Job { id: 1, retries_left: 6 }]);
}

#[test]
fn tick_twice() {
    let mut j = vec![Job { id: 1, retries_left: 2 }, Job { id: 2, retries_left: 3 }];
    tick(&mut j);
    tick(&mut j);
    check!(r#"jobs (id, retries_left) = [(1, 2), (2, 3)], two ticks"#, j, vec![Job { id: 2, retries_left: 1 }]);
}

#[test]
fn merge_one_long_run() {
    let mut r = vec![Run { key: 'x', count: 1 }, Run { key: 'x', count: 1 }, Run { key: 'x', count: 1 }, Run { key: 'x', count: 1 }, Run { key: 'x', count: 1 }];
    merge_runs(&mut r);
    check!(r#"runs = [(x, 1), (x, 1), (x, 1), (x, 1), (x, 1)]"#, r, vec![Run { key: 'x', count: 5 }]);
}

#[test]
fn merge_separated_runs_stay_apart() {
    let mut r = vec![Run { key: 'a', count: 1 }, Run { key: 'b', count: 1 }, Run { key: 'a', count: 1 }, Run { key: 'b', count: 1 }];
    merge_runs(&mut r);
    check!(r#"runs = [(a, 1), (b, 1), (a, 1), (b, 1)]"#, r, vec![Run { key: 'a', count: 1 }, Run { key: 'b', count: 1 }, Run { key: 'a', count: 1 }, Run { key: 'b', count: 1 }]);
}

#[test]
fn merge_empty() {
    let mut r = Vec::<Run>::new();
    merge_runs(&mut r);
    check!(r#"runs = []"#, r, Vec::<Run>::new());
}

#[test]
fn merge_zero_counts() {
    let mut r = vec![Run { key: 'a', count: 0 }, Run { key: 'a', count: 0 }, Run { key: 'b', count: 4 }, Run { key: 'b', count: 0 }];
    merge_runs(&mut r);
    check!(r#"runs = [(a, 0), (a, 0), (b, 4), (b, 0)]"#, r, vec![Run { key: 'a', count: 0 }, Run { key: 'b', count: 4 }]);
}

#[test]
fn same_minute_not_adjacent() {
    let mut e = vec![(0, "a".to_string()), (70, "b".to_string()), (10, "c".to_string())];
    first_per_minute(&mut e);
    check!(r#"events = [(0, "a"), (70, "b"), (10, "c")]"#, e, vec![(0, "a".to_string()), (70, "b".to_string()), (10, "c".to_string())]);
}

#[test]
fn minute_boundary() {
    let mut e = vec![(119, "a".to_string()), (120, "b".to_string()), (179, "c".to_string()), (180, "d".to_string())];
    first_per_minute(&mut e);
    check!(r#"events = [(119, "a"), (120, "b"), (179, "c"), (180, "d")]"#, e, vec![(119, "a".to_string()), (120, "b".to_string()), (180, "d".to_string())]);
}

#[test]
fn all_one_minute() {
    let mut e = vec![(3, "a".to_string()), (3, "b".to_string()), (30, "c".to_string())];
    first_per_minute(&mut e);
    check!(r#"events = [(3, "a"), (3, "b"), (30, "c")]"#, e, vec![(3, "a".to_string())]);
}

#[test]
fn no_events() {
    let mut e = Vec::<(u64, String)>::new();
    first_per_minute(&mut e);
    check!(r#"events = []"#, e, Vec::<(u64, String)>::new());
}

#[test]
fn large_timestamps() {
    let mut e = vec![(18446744073709551615, "a".to_string()), (18446744073709551600, "b".to_string())];
    first_per_minute(&mut e);
    check!(r#"events = [(18446744073709551615, "a"), (18446744073709551600, "b")]"#, e, vec![(18446744073709551615, "a".to_string())]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(7302);
    for _ in 0..400 {
        let n = rng.below(8);
        let js: Vec<Job> = (0..n).map(|i| Job { id: i as u32, retries_left: rng.below(4) as u32 }).collect();
        let want_jobs: Vec<Job> = js.iter().filter(|j| j.retries_left > 1).map(|j| Job { id: j.id, retries_left: j.retries_left - 1 }).collect();
        let rs: Vec<Run> = (0..n).map(|_| Run { key: *rng.pick(&['a', 'b']), count: rng.below(5) as u32 }).collect();
        let mut want_runs: Vec<Run> = Vec::new();
        for r in &rs {
            match want_runs.last_mut() {
                Some(last) if last.key == r.key => last.count += r.count,
                _ => want_runs.push(r.clone()),
            }
        }
        let es: Vec<(u64, String)> = (0..n).map(|i| (rng.below(200) as u64, i.to_string())).collect();
        let mut want_events: Vec<(u64, String)> = Vec::new();
        for e in &es {
            if want_events.last().map_or(true, |l| l.0 / 60 != e.0 / 60) {
                want_events.push(e.clone());
            }
        }
        let (mut a, mut b, mut c) = (js.clone(), rs.clone(), es.clone());
        tick(&mut a);
        merge_runs(&mut b);
        first_per_minute(&mut c);
        check!(format!("jobs = {js:?}, runs = {rs:?}, events = {es:?}"), (a, b, c), (want_jobs, want_runs, want_events));
    }
}

#[test]
fn scale_200k() {
    let mut j: Vec<Job> = (0..200_000).map(|i| Job { id: i, retries_left: i % 3 }).collect();
    tick(&mut j);
    let mut r: Vec<Run> = (0..200_000).map(|i| Run { key: if i < 100_000 { 'a' } else { 'b' }, count: 1 }).collect();
    merge_runs(&mut r);
    check!("200000 jobs and 200000 runs", (j.len(), j[0].id, r), (66_666, 2, vec![Run { key: 'a', count: 100_000 }, Run { key: 'b', count: 100_000 }]));
}
