use solution::*;

#[test]
fn leetcode_three() {
    check!(r#"cost = [10, 15, 20]"#, min_cost_climbing_stairs(&[10, 15, 20]), 15);
}

#[test]
fn leetcode_ten() {
    check!(r#"cost = [1, 100, 1, 1, 1, 100, 1, 1, 100, 1]"#, min_cost_climbing_stairs(&[1, 100, 1, 1, 1, 100, 1, 1, 100, 1]), 6);
}

#[test]
fn empty() {
    check!(r#"cost = []"#, min_cost_climbing_stairs(&[]), 0);
}

#[test]
fn one_step_is_free() {
    check!(r#"cost = [5] (start on step 1, which is the top)"#, min_cost_climbing_stairs(&[5]), 0);
}

#[test]
fn two_steps() {
    check!(r#"cost = [1, 2]"#, min_cost_climbing_stairs(&[1, 2]), 1);
}

#[test]
fn top_is_past_the_end() {
    check!(r#"cost = [3, 1, 1, 3]"#, min_cost_climbing_stairs(&[3, 1, 1, 3]), 2);
}
