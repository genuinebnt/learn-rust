use solution::*;

#[test]
fn empty() {
    check!(r#"nums = []"#, length_of_lis(&[]), 0);
}

#[test]
fn decreasing() {
    check!(r#"nums = [3, 2, 1]"#, length_of_lis(&[3, 2, 1]), 1);
}

#[test]
fn equal_not_increasing() {
    check!(r#"nums = [2, 2, 3, 3]"#, length_of_lis(&[2, 2, 3, 3]), 2);
}

#[test]
fn not_contiguous() {
    check!(r#"nums = [1, 3, 6, 7, 9, 4, 10, 5, 6]"#, length_of_lis(&[1, 3, 6, 7, 9, 4, 10, 5, 6]), 6);
}

#[test]
fn replace_middle() {
    check!(r#"nums = [1, 5, 2, 3]"#, length_of_lis(&[1, 5, 2, 3]), 3);
}

#[test]
fn extremes() {
    check!(r#"nums = [i32::MIN, i32::MAX]"#, length_of_lis(&[i32::MIN, i32::MAX]), 2);
}

#[test]
fn negatives() {
    check!(r#"nums = [-3, -5, -1, -2, 0]"#, length_of_lis(&[-3, -5, -1, -2, 0]), 3);
}

#[test]
fn increasing_200k() {
    check!(r#"nums = 0..200000"#, length_of_lis(&(0..200_000).collect::<Vec<i32>>()), 200_000);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1216);
    for _ in 0..400 {
        let n = rng.below(40);
        let nums: Vec<i32> = rng.vec(n, -8, 8);
        let mut ends_at = vec![1usize; n];
        for i in 0..n {
            for j in 0..i {
                if nums[j] < nums[i] {
                    ends_at[i] = ends_at[i].max(ends_at[j] + 1);
                }
            }
        }
        let want = ends_at.into_iter().max().unwrap_or(0);
        check!(format!("nums = {nums:?}"), length_of_lis(&nums), want);
    }
}

#[test]
fn scale_200k() {
    let nums: Vec<i32> = (0..200_000i64).map(|i| (i * 7919 % 100_003 - 50_000) as i32).collect();
    check!("nums[i] = (7919·i) % 100003 - 50000, 200000 values", length_of_lis(&nums), 511);
}

#[test]
fn scale_pairs_200k() {
    let nums: Vec<i32> = (0..200_000).map(|i| i / 2).collect();
    check!("nums = [0, 0, 1, 1, 2, 2, …] (200000 values)", length_of_lis(&nums), 100_000);
}
