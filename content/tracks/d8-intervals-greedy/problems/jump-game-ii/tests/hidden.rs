use solution::*;

#[test]
fn two_cells() {
    check!(r#"nums = [1, 0]"#, jump(&[1, 0]), Some(1));
}

#[test]
fn stuck_at_start() {
    check!(r#"nums = [0, 5]"#, jump(&[0, 5]), None);
}

#[test]
fn overshoot() {
    check!(r#"nums = [10, 0]"#, jump(&[10, 0]), Some(1));
}

#[test]
fn stuck_after_a_level() {
    check!(r#"nums = [1, 1, 0, 1]"#, jump(&[1, 1, 0, 1]), None);
}

#[test]
fn huge_jumps() {
    check!(r#"nums = [1000000000; 5]"#, jump(&[1_000_000_000; 5]), Some(1));
}

#[test]
fn window_edge() {
    check!(r#"nums = [2, 1, 1, 1]"#, jump(&[2, 1, 1, 1]), Some(2));
}

#[test]
fn three_levels() {
    check!(r#"nums = [1, 2, 1, 1, 1]"#, jump(&[1, 2, 1, 1, 1]), Some(3));
}

#[test]
fn exact_landing() {
    check!(r#"nums = [2, 0, 0]"#, jump(&[2, 0, 0]), Some(1));
}

#[test]
fn zero_on_the_last_index() {
    check!(r#"nums = [1, 1, 0]"#, jump(&[1, 1, 0]), Some(2));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(815);
    for _ in 0..400 {
        let n = 1 + rng.below(10);
        let nums: Vec<u32> = rng.vec(n, 0, 3);
        // dist[j]: fewest jumps to j, filled left to right.
        let mut dist: Vec<Option<usize>> = vec![None; n];
        dist[0] = Some(0);
        for i in 0..n {
            let Some(d) = dist[i] else { continue };
            for j in i + 1..=(i + nums[i] as usize).min(n - 1) {
                dist[j] = Some(dist[j].map_or(d + 1, |x| x.min(d + 1)));
            }
        }
        check!(format!("nums = {nums:?}"), jump(&nums), dist[n - 1]);
    }
}

#[test]
fn scale_200k() {
    let ones = vec![1u32; 200_000];
    let big = vec![200_000u32; 200_000];
    let stuck: Vec<u32> = (0..200_000u32).map(|i| 199_998u32.saturating_sub(i)).collect();
    check!("200000 ones; 200000 × 200000; nums[i] = 199998 - i", (jump(&ones), jump(&big), jump(&stuck)), (Some(199_999), Some(1), None));
}
