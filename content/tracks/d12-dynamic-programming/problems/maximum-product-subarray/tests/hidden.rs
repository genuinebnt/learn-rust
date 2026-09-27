use solution::*;

#[test]
fn empty() {
    check!(r#"nums = []"#, max_product(&[]), None);
}

#[test]
fn single_zero() {
    check!(r#"nums = [0]"#, max_product(&[0]), Some(0));
}

#[test]
fn single_negative() {
    check!(r#"nums = [-3]"#, max_product(&[-3]), Some(-3));
}

#[test]
fn negative_pair() {
    check!(r#"nums = [-2, -3]"#, max_product(&[-2, -3]), Some(6));
}

#[test]
fn odd_negatives() {
    check!(r#"nums = [-1, -1, -1]"#, max_product(&[-1, -1, -1]), Some(1));
}

#[test]
fn skip_the_negative() {
    check!(r#"nums = [3, -1, 4]"#, max_product(&[3, -1, 4]), Some(4));
}

#[test]
fn zero_splits() {
    check!(r#"nums = [-2, 0]"#, max_product(&[-2, 0]), Some(0));
}

#[test]
fn even_negatives_inside() {
    check!(r#"nums = [2, -5, -2, -4, 3]"#, max_product(&[2, -5, -2, -4, 3]), Some(24));
}

#[test]
fn before_a_zero() {
    check!(r#"nums = [-1, -2, -3, 0]"#, max_product(&[-1, -2, -3, 0]), Some(6));
}

#[test]
fn past_i32() {
    check!(r#"nums = [-10; 18]"#, max_product(&[-10; 18]), Some(1_000_000_000_000_000_000));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1214);
    for _ in 0..400 {
        let n = rng.below(11);
        let nums: Vec<i32> = rng.vec(n, -4, 4);
        let mut want: Option<i64> = None;
        for i in 0..n {
            let mut p = 1i64;
            for j in i..n {
                p *= nums[j] as i64;
                want = Some(want.map_or(p, |w| w.max(p)));
            }
        }
        check!(format!("nums = {nums:?}"), max_product(&nums), want);
    }
}

#[test]
fn scale_200k() {
    let mut nums = vec![1i32; 200_000];
    for i in (0..200_000).step_by(5_000) {
        nums[i] = -2;
    }
    nums[100_000] = 0;
    check!("nums = 200000 ones, -2 at every multiple of 5000, 0 at 100000", max_product(&nums), Some(1_048_576));
}
