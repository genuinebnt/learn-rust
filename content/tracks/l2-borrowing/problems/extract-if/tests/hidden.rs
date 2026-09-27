use solution::*;

fn queue(xs: &[(&str, u64)]) -> Queue {
    Queue { jobs: xs.iter().map(|&(n, d)| Job { name: n.to_string(), deadline: d }).collect() }
}

fn sv(xs: &[&str]) -> Vec<String> {
    xs.iter().map(|s| s.to_string()).collect()
}

fn names(jobs: &[Job]) -> Vec<String> {
    jobs.iter().map(|j| j.name.to_string()).collect()
}

#[test]
fn empty_queue() {
    let mut q = queue(&[]);
    check!(r#"empty queue: all three"#, (q.take_expired(9, 9).len(), q.next_batch(3).len(), q.defer("a")), (0, 0, false));
}

#[test]
fn nothing_expired() {
    let mut q = queue(&[("a", 5), ("b", 20), ("c", 7), ("d", 3), ("e", 50)]);
    check!(r#"jobs a 5, b 20, c 7, d 3, e 50; take_expired(now 0, limit 9)"#, (q.take_expired(0, 9).len(), q.jobs.len()), (0, 5));
}

#[test]
fn all_expired() {
    let mut q = queue(&[("a", 5), ("b", 20), ("c", 7), ("d", 3), ("e", 50)]);
    check!(r#"jobs a 5, b 20, c 7, d 3, e 50; take_expired(now 100, limit 9)"#, (names(&q.take_expired(100, 9)), q.jobs.len()), (sv(&["a", "b", "c", "d", "e"]), 0));
}

#[test]
fn batch_zero() {
    let mut q = queue(&[("a", 5), ("b", 20), ("c", 7), ("d", 3), ("e", 50)]);
    check!(r#"jobs a 5, b 20, c 7, d 3, e 50; next_batch(0)"#, (q.next_batch(0).len(), q.jobs.len()), (0, 5));
}

#[test]
fn defer_last_is_noop() {
    let mut q = queue(&[("a", 5), ("b", 20), ("c", 7), ("d", 3), ("e", 50)]);
    check!(r#"jobs a 5, b 20, c 7, d 3, e 50; defer("e")"#, (q.defer("e"), names(&q.jobs)), (true, sv(&["a", "b", "c", "d", "e"])));
}

#[test]
fn defer_first_duplicate() {
    let mut q = queue(&[("x", 1), ("y", 2), ("x", 3)]);
    check!(r#"jobs x 1, y 2, x 3; defer("x")"#, (q.defer("x"), q.jobs.iter().map(|j| j.deadline).collect::<Vec<_>>()), (true, vec![2, 3, 1]));
}

#[test]
fn jobs_moved_not_copied() {
    let mut q = queue(&[("k", 1)]);
    let p = q.jobs[0].name.as_ptr();
    let got = q.take_expired(2, 1);
    check!(r#"take_expired keeps the job's own String"#, (got[0].name.as_ptr() == p, got.len()), (true, 1));
}

#[test]
fn take_expired_twice() {
    let mut q = queue(&[("a", 5), ("b", 20), ("c", 7), ("d", 3), ("e", 50)]);
    check!(r#"jobs a 5, b 20, c 7, d 3, e 50; take_expired(now 10, limit 1) twice"#, { let a = q.take_expired(10, 1); let b = q.take_expired(10, 1); (names(&a), names(&b), names(&q.jobs)) }, (sv(&["a"]), sv(&["c"]), sv(&["b", "d", "e"])));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6222);
    for _ in 0..300 {
        let n = rng.below(8);
        let start: Vec<(String, u64)> = (0..n).map(|i| (format!("{}{i}", rng.string(1, "ab")), rng.below(10) as u64)).collect();
        let mut q = Queue { jobs: start.iter().map(|(s, d)| Job { name: s.clone(), deadline: *d }).collect() };
        let mut model = start.clone();
        let mut ops = Vec::new();
        for _ in 0..4 {
            match rng.below(3) {
                0 => {
                    let (now, limit) = (rng.below(10) as u64, rng.below(4));
                    let mut want = Vec::new();
                    let mut kept = Vec::new();
                    for (s, d) in model {
                        if d < now && want.len() < limit {
                            want.push(s);
                        } else {
                            kept.push((s, d));
                        }
                    }
                    model = kept;
                    ops.push(format!("take_expired({now}, {limit})"));
                    let got: Vec<String> = q.take_expired(now, limit).into_iter().map(|j| j.name).collect();
                    check!(format!("{start:?}; {}", ops.join(", ")), got, want);
                }
                1 => {
                    let k = rng.below(4);
                    let want: Vec<String> = model.drain(..k.min(model.len())).map(|(s, _)| s).collect();
                    ops.push(format!("next_batch({k})"));
                    let got: Vec<String> = q.next_batch(k).into_iter().map(|j| j.name).collect();
                    check!(format!("{start:?}; {}", ops.join(", ")), got, want);
                }
                _ => {
                    let name = format!("{}{}", rng.string(1, "ab"), rng.below(n + 1));
                    let want = match model.iter().position(|(s, _)| *s == name) {
                        Some(i) => {
                            let j = model.remove(i);
                            model.push(j);
                            true
                        }
                        None => false,
                    };
                    ops.push(format!("defer({name:?})"));
                    check!(format!("{start:?}; {}", ops.join(", ")), q.defer(&name), want);
                }
            }
        }
        let got: Vec<(String, u64)> = q.jobs.iter().map(|j| (j.name.clone(), j.deadline)).collect();
        check!(format!("{start:?}; {}; queue", ops.join(", ")), got, model);
    }
}

#[test]
fn long_queue() {
    let mut q = Queue { jobs: (0..200_000).map(|i| Job { name: format!("j{i}"), deadline: i % 2 }).collect() };
    let gone = q.take_expired(1, 150_000);
    let batch = q.next_batch(1);
    let deferred = q.defer("j1");
    check!("200000 jobs, half expired", (gone.len(), gone[99_999].name.clone(), batch[0].name.clone(), deferred, q.jobs.len(), q.jobs[99_998].name.clone()), (100_000, "j199998".to_string(), "j1".to_string(), false, 99_999, "j199999".to_string()));
}
