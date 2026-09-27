use solution::*;

#[test]
fn mixed() {
    check!(r#"costs c 1, a 2, b 1, d 0"#, run_order(vec![Job { cost: 1, name: "c" }, Job { cost: 2, name: "a" }, Job { cost: 1, name: "b" }, Job { cost: 0, name: "d" }]), vec!["d", "b", "c", "a"]);
}

#[test]
fn consistent_with_eq() {
    check!(r#"two jobs, same cost, different names"#, Job { cost: 1, name: "a" }.cmp(&Job { cost: 1, name: "b" }) != std::cmp::Ordering::Equal, true);
}

#[test]
fn zero_and_max_cost() {
    check!(r#"costs max u32::MAX, zero 0, mid 5"#, run_order(vec![Job { cost: u32::MAX, name: "max" }, Job { cost: 0, name: "zero" }, Job { cost: 5, name: "mid" }]), vec!["zero", "mid", "max"]);
}

#[test]
fn equal_jobs_compare_equal() {
    check!(r#"the same job twice"#, Job { cost: 3, name: "x" }.cmp(&Job { cost: 3, name: "x" }), std::cmp::Ordering::Equal);
}

#[test]
fn partial_cmp_agrees_with_cmp() {
    let (a, b) = (Job { cost: 1, name: "b" }, Job { cost: 1, name: "a" });
    let (c, d) = (Job { cost: 2, name: "a" }, Job { cost: 1, name: "z" });
    check!(r#"cost 1 'b' vs cost 1 'a', and cost 2 'a' vs cost 1 'z'"#, (a.partial_cmp(&b) == Some(a.cmp(&b)), c.partial_cmp(&d) == Some(c.cmp(&d)), a.cmp(&b)), (true, true, std::cmp::Ordering::Less));
}

#[test]
fn ties_at_several_costs() {
    check!(r#"costs b 2, a 2, d 1, c 1"#, run_order(vec![Job { cost: 2, name: "b" }, Job { cost: 2, name: "a" }, Job { cost: 1, name: "d" }, Job { cost: 1, name: "c" }]), vec!["c", "d", "a", "b"]);
}

#[test]
fn many_ties_in_reverse() {
    check!(r#"five jobs of cost 1 named e, d, c, b, a, then one of cost 0 named z"#, run_order(vec![Job { cost: 1, name: "e" }, Job { cost: 1, name: "d" }, Job { cost: 1, name: "c" }, Job { cost: 1, name: "b" }, Job { cost: 1, name: "a" }, Job { cost: 0, name: "z" }]), vec!["z", "a", "b", "c", "d", "e"]);
}

#[test]
fn random_vs_brute_force() {
    let names = ["alpha", "beta", "gamma", "delta", "eps", "zeta", "eta", "theta"];
    let mut rng = anneal_prelude::Rng::new(916);
    for _ in 0..300 {
        let n = rng.below(10);
        let jobs: Vec<(u32, &'static str)> = (0..n).map(|_| (rng.int(0, 4) as u32, *rng.pick(&names))).collect();
        let mut sorted = jobs.clone();
        sorted.sort();
        let want: Vec<&str> = sorted.iter().map(|j| j.1).collect();
        let got = run_order(jobs.iter().map(|&(cost, name)| Job { cost, name }).collect());
        check!(format!("jobs (cost, name) = {jobs:?}"), got, want);
    }
}
