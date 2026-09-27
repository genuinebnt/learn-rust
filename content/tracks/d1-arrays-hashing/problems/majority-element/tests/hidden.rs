use solution::*;

#[test]
fn single() {
    check!(r#"nums = [9]"#, majority(&[9]), 9);
}

#[test]
fn negative_majority() {
    check!(r#"nums = [-1, 5, -1, -1, 6]"#, majority(&[-1, 5, -1, -1, 6]), -1);
}

#[test]
fn all_same() {
    check!(r#"nums = [4, 4, 4, 4]"#, majority(&[4, 4, 4, 4]), 4);
}

#[test]
fn pair() {
    check!(r#"nums = [5, 5]"#, majority(&[5, 5]), 5);
}

#[test]
fn majority_at_end() {
    check!(r#"nums = [1, 2, 3, 2, 2]"#, majority(&[1, 2, 3, 2, 2]), 2);
}

#[test]
fn majority_at_start() {
    check!(r#"nums = [7, 7, 7, 1, 2]"#, majority(&[7, 7, 7, 1, 2]), 7);
}

#[test]
fn extremes() {
    check!(r#"nums = [i32::MIN, i32::MAX, i32::MIN]"#, majority(&[i32::MIN, i32::MAX, i32::MIN]), i32::MIN);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(7);
    for _ in 0..300 {
        let n = 1 + rng.below(15);
        let m = rng.int(-5, 5) as i32;
        let copies = n / 2 + 1 + rng.below(n - n / 2);
        let mut nums: Vec<i32> = vec![m; copies];
        while nums.len() < n {
            nums.push(rng.int(-5, 5) as i32);
        }
        rng.shuffle(&mut nums);
        let want = *nums.iter().find(|&&x| nums.iter().filter(|&&y| y == x).count() * 2 > n).unwrap();
        check!(format!("nums = {nums:?}"), majority(&nums), want);
    }
}

#[test]
fn scale_200k() {
    let mut nums: Vec<i32> = (0..100_000).collect();
    nums.extend(vec![-3; 100_001]);
    check!("nums = 0..100000, then -3 × 100001", majority(&nums), -3);
}
