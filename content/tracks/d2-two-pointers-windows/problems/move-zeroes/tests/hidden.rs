use solution::*;

#[test]
fn no_zeroes() {
    check!(r#"nums = [1, 2, 3]"#, { let mut v = [1, 2, 3]; move_zeroes(&mut v); v }, [1, 2, 3]);
}

#[test]
fn negatives() {
    check!(r#"nums = [-1, 0, 0, -2]"#, { let mut v = [-1, 0, 0, -2]; move_zeroes(&mut v); v }, [-1, -2, 0, 0]);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, { let mut v: [i32; 0] = []; move_zeroes(&mut v); v }, [0i32; 0]);
}

#[test]
fn all_zeroes() {
    check!(r#"nums = [0, 0, 0]"#, { let mut v = [0, 0, 0]; move_zeroes(&mut v); v }, [0, 0, 0]);
}

#[test]
fn already_at_end() {
    check!(r#"nums = [4, 5, 0, 0]"#, { let mut v = [4, 5, 0, 0]; move_zeroes(&mut v); v }, [4, 5, 0, 0]);
}

#[test]
fn single_value() {
    check!(r#"nums = [7]"#, { let mut v = [7]; move_zeroes(&mut v); v }, [7]);
}

#[test]
fn order_kept() {
    check!(r#"nums = [0, 3, 0, 1, 0, 2]"#, { let mut v = [0, 3, 0, 1, 0, 2]; move_zeroes(&mut v); v }, [3, 1, 2, 0, 0, 0]);
}

#[test]
fn duplicates() {
    check!(r#"nums = [2, 0, 2, 0, 2]"#, { let mut v = [2, 0, 2, 0, 2]; move_zeroes(&mut v); v }, [2, 2, 2, 0, 0]);
}

#[test]
fn extremes() {
    check!(r#"nums = [0, i32::MIN, 0, i32::MAX]"#, { let mut v = [0, i32::MIN, 0, i32::MAX]; move_zeroes(&mut v); v }, [i32::MIN, i32::MAX, 0, 0]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(204);
    for _ in 0..300 {
        let n = rng.below(12);
        let nums: Vec<i32> = rng.vec(n, -3, 3);
        let mut want: Vec<i32> = nums.iter().copied().filter(|&x| x != 0).collect();
        want.resize(n, 0);
        let mut got = nums.clone();
        move_zeroes(&mut got);
        check!(format!("nums = {nums:?}"), got, want);
    }
}

#[test]
fn scale_200k() {
    let n = 200_000;
    let mut nums = vec![0; n];
    for i in n / 2..n {
        nums[i] = (i - n / 2 + 1) as i32;
    }
    move_zeroes(&mut nums);
    let mut want: Vec<i32> = (1..=(n / 2) as i32).collect();
    want.resize(n, 0);
    check!("nums = [0; 100000] followed by 1..=100000", nums == want, true);
}
