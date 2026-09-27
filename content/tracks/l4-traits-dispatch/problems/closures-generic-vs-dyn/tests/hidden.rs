use solution::*;

#[test]
fn apply_n_zero_times() {
    check!(r#"apply_n(9, 0, |x| x + 1)"#, apply_n(9, 0, |x| x + 1), 9);
}

#[test]
fn apply_n_stateful() {
    let mut k = 0;
    check!(r#"apply_n(0, 4, add 1, 2, 3, 4)"#, apply_n(0, 4, |x| {
        k += 1;
        x + k
    }), 10);
}

#[test]
fn apply_n_dyn_zero_calls() {
    let mut calls = 0;
    let mut f = |x: i64| {
        calls += 1;
        x
    };
    check!(r#"apply_n_dyn(5, 0, ..) doesn't call f"#, (apply_n_dyn(5, 0, &mut f), calls), (5, 0));
}

#[test]
fn empty_pipeline() {
    let mut p = Pipeline::new();
    check!(r#"Pipeline::new().run(4)"#, (p.run(4), p.len()), (4, 0));
}

#[test]
fn state_kept_between_runs() {
    let mut p = Pipeline::new();
    let mut total = 0;
    p.push(move |x| {
        total += x;
        total
    });
    check!(r#"running total step; run(1), run(2), run(3)"#, (p.run(1), p.run(2), p.run(3)), (1, 3, 6));
}

#[test]
fn order_matters() {
    let mut p = Pipeline::new();
    p.push(|x| x * 2).push(|x| x + 1);
    check!(r#"push(*2), push(+1); run(5)"#, p.run(5), 11);
}

#[test]
fn len_counts_steps() {
    let mut p = Pipeline::new();
    p.push(|x| x).push(|x| x).push(|x| -x);
    check!(r#"three pushes"#, p.len(), 3);
}

#[test]
fn moved_owned_state() {
    let offsets = vec![1, 2, 3];
    let mut p = Pipeline::new();
    p.push(move |x| x + offsets.iter().sum::<i64>());
    check!(r#"a step owning a Vec of offsets"#, p.run(0), 6);
}

#[test]
fn pipeline_is_send() {
    fn assert_send<T: Send>(_: &T) {}
    let mut hits = 0;
    let mut p = Pipeline::new();
    p.push(|x| {
        hits += 1;
        x - 1
    });
    assert_send(&p);
    let got = std::thread::scope(|s| s.spawn(move || p.run(10)).join().unwrap());
    check!("run(10) on another thread, then hits", (got, hits), (9, 1));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4407);
    for _ in 0..300 {
        let n = rng.below(6);
        let ops: Vec<(bool, i64)> = (0..n).map(|_| (rng.bool(), rng.int(-3, 3))).collect();
        let start = rng.int(-10, 10);
        let mut p = Pipeline::new();
        for &(add, k) in &ops {
            if add {
                p.push(move |x| x + k);
            } else {
                p.push(move |x| x * k);
            }
        }
        let want = ops.iter().fold(start, |x, &(add, k)| if add { x + k } else { x * k });
        check!(format!("ops = {ops:?}, start = {start}"), p.run(start), want);
        let times = rng.below(8) as u32;
        check!(format!("apply_n({start}, {times}, +3)"), apply_n(start, times, |x| x + 3), start + 3 * times as i64);
    }
}
