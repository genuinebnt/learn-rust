use solution::*;

#[test]
fn empty_run() {
    let s = Scheduler::new();
    check!(r#"run on a new scheduler"#, (s.run(), s.done()), (0, vec![]));
}

#[test]
fn zero_job() {
    let s = Scheduler::new();
    s.submit(0);
    check!(r#"submit 0; run"#, (s.run(), s.done()), (1, vec![0]));
}

#[test]
fn power_of_two() {
    let s = Scheduler::new();
    s.submit(16);
    check!(r#"submit 16; run"#, (s.run(), s.done()), (5, vec![16, 8, 4, 2, 1]));
}

#[test]
fn run_twice() {
    let s = Scheduler::new();
    s.submit(4);
    check!(r#"submit 4; run; submit 4, 9; run"#, { s.run(); s.submit(4); s.submit(9); (s.run(), s.done()) }, (1, vec![4, 2, 1, 9]));
}

#[test]
fn count_after_run() {
    let s = Scheduler::new();
    s.submit(8);
    check!(r#"submit 8; run; count 8, 4, 2, 1"#, { s.run(); (s.count(8), s.count(4), s.count(2), s.count(1)) }, (1, 1, 1, 1));
}

#[test]
fn count_seeds_once() {
    let s = Scheduler::new();
    check!(r#"count 5 twice, then submit 5"#, (s.count(5), s.count(5), s.submit(5), s.count(5)), (0, 0, false, 1));
}

#[test]
fn known_counts_entries() {
    let s = Scheduler::new();
    check!(r#"submit 1, 1, 2; count 7"#, { s.submit(1); s.submit(1); s.submit(2); s.count(7); s.known() }, 3);
}

#[test]
fn big_job() {
    let s = Scheduler::new();
    s.submit(u32::MAX - 1);
    check!(r#"submit u32::MAX - 1 (even); run"#, (s.run(), s.done()[1]), (2, u32::MAX / 2));
}

#[test]
fn random_vs_model() {
    use std::collections::HashMap;
    let mut rng = anneal_prelude::Rng::new(6234);
    for _ in 0..300 {
        let s = Scheduler::new();
        let (mut queue, mut seen, mut done): (Vec<u32>, HashMap<u32, u32>, Vec<u32>) = (vec![], HashMap::new(), vec![]);
        let mut ops = Vec::new();
        fn submit(queue: &mut Vec<u32>, seen: &mut HashMap<u32, u32>, job: u32) -> bool {
            let first = !seen.contains_key(&job);
            *seen.entry(job).or_insert(0) += 1;
            if first {
                queue.push(job);
            }
            first
        }
        for _ in 0..6 {
            match rng.below(3) {
                0 => {
                    let j = rng.below(20) as u32;
                    ops.push(format!("submit {j}"));
                    check!(ops.join(", "), s.submit(j), submit(&mut queue, &mut seen, j));
                }
                1 => {
                    let j = rng.below(20) as u32;
                    let want = *seen.entry(j).or_insert(0);
                    ops.push(format!("count {j}"));
                    check!(ops.join(", "), s.count(j), want);
                }
                _ => {
                    let mut ran = 0;
                    while let Some(j) = queue.pop() {
                        done.push(j);
                        if j > 0 && j % 2 == 0 {
                            submit(&mut queue, &mut seen, j / 2);
                        }
                        ran += 1;
                    }
                    ops.push("run".to_string());
                    check!(ops.join(", "), s.run(), ran);
                }
            }
        }
        check!(format!("{}; done, known", ops.join(", ")), (s.done(), s.known()), (done, seen.len()));
    }
}
