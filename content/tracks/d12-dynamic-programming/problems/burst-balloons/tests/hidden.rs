use solution::*;

#[test]
fn empty() {
    check!(r#"nums = []"#, max_coins(&[]), 0);
}

#[test]
fn zero_and_one() {
    check!(r#"nums = [0, 1]"#, max_coins(&[0, 1]), 1);
}

#[test]
fn four_big() {
    check!(r#"nums = [9, 76, 64, 21]"#, max_coins(&[9, 76, 64, 21]), 116_718);
}

#[test]
fn max_values() {
    check!(r#"nums = [100, 100, 100]"#, max_coins(&[100, 100, 100]), 1_010_100);
}

#[test]
fn with_zeros() {
    check!(r#"nums = [8, 2, 6, 8, 9, 8, 1, 4, 1, 5, 3, 0, 7, 7, 0, 4, 2, 2, 5]"#, max_coins(&[8, 2, 6, 8, 9, 8, 1, 4, 1, 5, 3, 0, 7, 7, 0, 4, 2, 2, 5]), 3630);
}

#[test]
fn single_zero() {
    check!(r#"nums = [0]"#, max_coins(&[0]), 0);
}

#[test]
fn all_zero() {
    check!(r#"nums = [0, 0, 0]"#, max_coins(&[0, 0, 0]), 0);
}

#[test]
fn random_vs_brute_force() {
    fn best(v: &mut Vec<u64>) -> u64 {
        let mut top = 0;
        for k in 0..v.len() {
            let left = if k > 0 { v[k - 1] } else { 1 };
            let right = if k + 1 < v.len() { v[k + 1] } else { 1 };
            let x = v.remove(k);
            top = top.max(left * x * right + best(v));
            v.insert(k, x);
        }
        top
    }
    let mut rng = anneal_prelude::Rng::new(1245);
    for _ in 0..200 {
        let n = rng.below(7);
        let nums: Vec<u32> = rng.vec(n, 0, 9);
        let mut v: Vec<u64> = nums.iter().map(|&x| x as u64).collect();
        check!(format!("nums = {nums:?}"), max_coins(&nums), best(&mut v));
    }
}

#[test]
fn scale_300() {
    let nums: Vec<u32> = (0..300u32).map(|i| i * 7919 % 100 + 1).collect();
    check!("nums[i] = (7919·i) % 100 + 1, 300 balloons", max_coins(&nums), 112_945_464);
}
