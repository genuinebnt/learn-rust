use solution::*;

#[test]
fn empty() {
    check!(r#"nums = []"#, length_of_lis(&[]), 0);
}

#[test]
fn single() {
    check!(r#"nums = [-4]"#, length_of_lis(&[-4]), 1);
}

#[test]
fn increasing() {
    check!(r#"nums = [1, 2, 3]"#, length_of_lis(&[1, 2, 3]), 3);
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
fn restart_trap() {
    check!(r#"nums = [4, 10, 4, 3, 8, 9]"#, length_of_lis(&[4, 10, 4, 3, 8, 9]), 3);
}

#[test]
fn extremes() {
    check!(r#"nums = [i32::MIN, i32::MAX]"#, length_of_lis(&[i32::MIN, i32::MAX]), 2);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1215);
    for _ in 0..300 {
        let n = rng.below(12);
        let nums: Vec<i32> = rng.vec(n, -5, 5);
        let mut want = 0;
        for mask in 0u32..(1 << n) {
            let picked: Vec<i32> = (0..n).filter(|&i| mask >> i & 1 == 1).map(|i| nums[i]).collect();
            if picked.windows(2).all(|w| w[0] < w[1]) {
                want = want.max(picked.len());
            }
        }
        check!(format!("nums = {nums:?}"), length_of_lis(&nums), want);
    }
}

#[test]
fn scale_2500() {
    let nums: Vec<i32> = (0..2500i64).map(|i| (i * 7919 % 10_007 - 5_000) as i32).collect();
    check!("nums[i] = (7919·i) % 10007 - 5000, 2500 values", length_of_lis(&nums), 44);
}
