use solution::*;

#[test]
fn leetcode_four() {
    check!(r#"costs = [(10, 20), (30, 200), (400, 50), (30, 20)]"#, two_city_sched_cost(&[(10, 20), (30, 200), (400, 50), (30, 20)]), 110);
}

#[test]
fn leetcode_six() {
    check!(r#"costs = [(259, 770), (448, 54), (926, 667), (184, 139), (840, 118), (577, 469)]"#, two_city_sched_cost(&[(259, 770), (448, 54), (926, 667), (184, 139), (840, 118), (577, 469)]), 1859);
}

#[test]
fn leetcode_eight() {
    check!(r#"costs = [(515, 563), (451, 713), (537, 709), (343, 819), (855, 779), (457, 60), (650, 359), (631, 42)]"#, two_city_sched_cost(&[(515, 563), (451, 713), (537, 709), (343, 819), (855, 779), (457, 60), (650, 359), (631, 42)]), 3086);
}

#[test]
fn nobody() {
    check!(r#"costs = []"#, two_city_sched_cost(&[]), 0);
}

#[test]
fn half_must_go_to_each() {
    check!(r#"costs = [(1, 100), (1, 100)]"#, two_city_sched_cost(&[(1, 100), (1, 100)]), 101);
}
