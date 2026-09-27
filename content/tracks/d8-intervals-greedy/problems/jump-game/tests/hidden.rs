use solution::*;

#[test]
fn two_ones() {
    check!(r#"nums = [1, 1]"#, can_jump(&[1, 1]), true);
}

#[test]
fn zero_in_the_middle() {
    check!(r#"nums = [1, 0, 1]"#, can_jump(&[1, 0, 1]), false);
}

#[test]
fn zero_at_the_end() {
    check!(r#"nums = [1, 1, 0]"#, can_jump(&[1, 1, 0]), true);
}

#[test]
fn one_short() {
    check!(r#"nums = [3, 0, 0, 0, 1]"#, can_jump(&[3, 0, 0, 0, 1]), false);
}

#[test]
fn just_enough() {
    check!(r#"nums = [4, 0, 0, 0, 1]"#, can_jump(&[4, 0, 0, 0, 1]), true);
}

#[test]
fn later_index_reaches_further() {
    check!(r#"nums = [1, 2, 0, 0, 1]"#, can_jump(&[1, 2, 0, 0, 1]), false);
}

#[test]
fn huge_jump() {
    check!(r#"nums = [1000000000, 0, 0, 0]"#, can_jump(&[1_000_000_000, 0, 0, 0]), true);
}

#[test]
fn all_zeros() {
    check!(r#"nums = [0; 100]"#, can_jump(&vec![0; 100]), false);
}

#[test]
fn relay() {
    check!(r#"nums = [2, 5, 0, 0, 0, 0, 1]"#, can_jump(&[2, 5, 0, 0, 0, 0, 1]), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(814);
    for _ in 0..400 {
        let n = 1 + rng.below(10);
        let nums: Vec<u32> = rng.vec(n, 0, 3);
        // Mark every index each reachable index can land on.
        let mut ok = vec![false; n];
        ok[0] = true;
        for i in 0..n {
            if ok[i] {
                for j in i + 1..=(i + nums[i] as usize).min(n - 1) {
                    ok[j] = true;
                }
            }
        }
        check!(format!("nums = {nums:?}"), can_jump(&nums), ok[n - 1]);
    }
}

#[test]
fn scale_200k() {
    // nums[i] = 199998 - i: every jump lands at or before index 199998, which holds 0.
    let n = 200_000u32;
    let stuck: Vec<u32> = (0..n).map(|i| (n - 2).saturating_sub(i)).collect();
    let mut fixed = stuck.clone();
    fixed[0] = n - 1;
    check!("nums[i] = 199998 - i (then zeros); then with nums[0] = 199999", (can_jump(&stuck), can_jump(&fixed)), (false, true));
}
