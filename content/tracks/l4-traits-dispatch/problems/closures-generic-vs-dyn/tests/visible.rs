use solution::*;

#[test]
fn apply_n_doubles() {
    check!(r#"apply_n(1, 5, |x| x * 2)"#, apply_n(1, 5, |x| x * 2), 32);
}

#[test]
fn apply_n_dyn_counts_calls() {
    let mut calls = 0;
    let mut counting = |x: i64| {
        calls += 1;
        x + 1
    };
    check!(r#"apply_n_dyn(0, 3, &mut counting), then calls"#, (apply_n_dyn(0, 3, &mut counting), calls), (3, 3));
}

#[test]
fn pipeline_in_push_order() {
    let mut p = Pipeline::new();
    p.push(|x| x + 1).push(|x| x * 2);
    check!(r#"push(+1), push(*2); run(5)"#, p.run(5), 12);
}

#[test]
fn steps_borrow_locals() {
    let mut seen = Vec::new();
    {
        let mut p = Pipeline::new();
        p.push(|x| {
            seen.push(x);
            x
        });
        p.run(1);
        p.run(10);
    }
    check!(r#"a step pushes every input into a local Vec; run(1), run(10)"#, seen, vec![1, 10]);
}

#[test]
fn runs_on_another_thread() {
    let mut p = Pipeline::new();
    p.push(|x| x * 3);
    check!(r#"push(*3); run(7) on a scoped thread"#, std::thread::scope(|s| s.spawn(|| p.run(7)).join().unwrap()), 21);
}
