use solution::*;

#[test]
fn peak_then_plateau() {
    check!(r#"ratings = [1, 3, 2, 2, 1]"#, candy(&[1, 3, 2, 2, 1]), 7);
}

#[test]
fn mountain() {
    check!(r#"ratings = [1, 2, 3, 2, 1]"#, candy(&[1, 2, 3, 2, 1]), 9);
}

#[test]
fn long_rise_short_fall() {
    check!(r#"ratings = [1, 3, 4, 5, 2]"#, candy(&[1, 3, 4, 5, 2]), 11);
}

#[test]
fn fall_rise_fall() {
    check!(r#"ratings = [5, 4, 3, 5, 6, 2]"#, candy(&[5, 4, 3, 5, 6, 2]), 12);
}

#[test]
fn short_rise_long_fall() {
    check!(r#"ratings = [1, 6, 10, 8, 7, 3, 2]"#, candy(&[1, 6, 10, 8, 7, 3, 2]), 18);
}

#[test]
fn plateau_top() {
    check!(r#"ratings = [1, 2, 87, 87, 87, 2, 1]"#, candy(&[1, 2, 87, 87, 87, 2, 1]), 13);
}

#[test]
fn negatives() {
    check!(r#"ratings = [-5, -10, -10, 3]"#, candy(&[-5, -10, -10, 3]), 6);
}

#[test]
fn i32_extremes() {
    check!(r#"ratings = [-2147483648, 2147483647, -2147483648]"#, candy(&[i32::MIN, i32::MAX, i32::MIN]), 4);
}

#[test]
fn two_rising() {
    check!(r#"ratings = [1, 2]"#, candy(&[1, 2]), 3);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(825);
    for _ in 0..400 {
        let n = rng.below(10);
        let ratings: Vec<i32> = rng.vec(n, -2, 3);
        // Raise any child that breaks a rule until nobody does.
        let mut give = vec![1u64; n];
        loop {
            let mut changed = false;
            for i in 0..n {
                for j in [i.wrapping_sub(1), i + 1] {
                    if j < n && ratings[i] > ratings[j] && give[i] <= give[j] {
                        give[i] = give[j] + 1;
                        changed = true;
                    }
                }
            }
            if !changed {
                break;
            }
        }
        check!(format!("ratings = {ratings:?}"), candy(&ratings), give.iter().sum::<u64>());
    }
}

#[test]
fn scale_200k() {
    let falling: Vec<i32> = (0..200_000).rev().collect();
    let rising: Vec<i32> = (0..200_000).collect();
    check!("199999 down to 0; 0 up to 199999", (candy(&falling), candy(&rising)), (20_000_100_000, 20_000_100_000));
}
