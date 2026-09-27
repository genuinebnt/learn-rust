use solution::*;

#[test]
fn none() {
    check!(r#"deadline 50; now 10"#, { let mut v = vec![Job { name: "a", deadline: 50 }]; take_expired(&mut v, 10).len() }, 0);
}

#[test]
fn now_zero() {
    check!(r#"deadline 0; now 0"#, { let mut v = vec![Job { name: "a", deadline: 0 }]; (take_expired(&mut v, 0).len(), v.len()) }, (0, 1));
}

#[test]
fn u64_max() {
    check!(r#"deadline u64::MAX - 1; now u64::MAX"#, { let mut v = vec![Job { name: "a", deadline: u64::MAX - 1 }, Job { name: "b", deadline: u64::MAX }]; let gone = take_expired(&mut v, u64::MAX); (gone.len(), v[0].name) }, (1, "b"));
}

#[test]
fn same_deadlines() {
    check!(r#"deadlines 5, 5; now 6"#, { let mut v = vec![Job { name: "a", deadline: 5 }, Job { name: "b", deadline: 5 }]; let gone = take_expired(&mut v, 6); (gone.len(), v.len()) }, (2, 0));
}

#[test]
fn returns_the_jobs() {
    check!(r#"deadlines 1, 20; now 10"#, { let mut v = vec![Job { name: "a", deadline: 1 }, Job { name: "b", deadline: 20 }]; take_expired(&mut v, 10) }, vec![Job { name: "a", deadline: 1 }]);
}

#[test]
fn many() {
    check!(r#"1000 jobs with deadlines 0..1000; now 500"#, { let mut v: Vec<Job> = (0..1000).map(|d| Job { name: "j", deadline: d }).collect(); let gone = take_expired(&mut v, 500); (gone.len(), v.len(), gone[499].deadline, v[0].deadline) }, (500, 500, 499, 500));
}

#[test]
fn called_twice() {
    check!(r#"deadlines 3, 7; now 5 then 8"#, { let mut v = vec![Job { name: "a", deadline: 3 }, Job { name: "b", deadline: 7 }]; let x = take_expired(&mut v, 5).len(); let y = take_expired(&mut v, 8).len(); (x, y, v.len()) }, (1, 1, 0));
}

#[test]
fn random_vs_model() {
    const NAMES: [&str; 5] = ["a", "b", "c", "d", "e"];
    let mut rng = anneal_prelude::Rng::new(2020);
    for _ in 0..300 {
        let n = rng.below(8);
        let specs: Vec<(&'static str, u64)> = (0..n).map(|_| { let name = *rng.pick(&NAMES); (name, rng.below(10) as u64) }).collect();
        let now = rng.below(11) as u64;
        let make = |keep: bool| -> Vec<Job> { specs.iter().filter(|s| (s.1 < now) != keep).map(|&(name, deadline)| Job { name, deadline }).collect() };
        let mut jobs: Vec<Job> = specs.iter().map(|&(name, deadline)| Job { name, deadline }).collect();
        let gone = take_expired(&mut jobs, now);
        check!(format!("jobs = {specs:?}, now = {now}"), (gone, jobs), (make(false), make(true)));
    }
}

#[test]
fn scale_300k_expired_first() {
    let mut v: Vec<Job> = (0..300_000u64).map(|i| Job { name: "j", deadline: if i < 150_000 { i } else { 1_000_000 + i } }).collect();
    let gone = take_expired(&mut v, 150_000);
    check!("150000 expired jobs then 150000 live ones", (gone.len(), v.len(), gone[149_999].deadline, v[0].deadline), (150_000, 150_000, 149_999, 1_150_000));
}
