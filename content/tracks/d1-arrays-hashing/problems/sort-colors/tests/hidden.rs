use solution::*;

#[test]
fn empty() {
    check!(r#"nums = []"#, { let mut v: Vec<u8> = vec![]; sort_colors(&mut v); v }, Vec::<u8>::new());
}

#[test]
fn all_twos() {
    check!(r#"nums = [2, 2, 2]"#, { let mut v = vec![2, 2, 2]; sort_colors(&mut v); v }, vec![2, 2, 2]);
}

#[test]
fn long() {
    check!(r#"nums = [2, 1, 0] × 1000"#, { let mut v: Vec<u8> = [2, 1, 0].repeat(1000); sort_colors(&mut v); (v[999], v[1000], v[2000], v[2999]) }, (0, 1, 2, 2));
}

#[test]
fn single() {
    check!(r#"nums = [1]"#, { let mut v = vec![1]; sort_colors(&mut v); v }, vec![1]);
}

#[test]
fn pair() {
    check!(r#"nums = [1, 0]"#, { let mut v = vec![1, 0]; sort_colors(&mut v); v }, vec![0, 1]);
}

#[test]
fn already_sorted() {
    check!(r#"nums = [0, 0, 1, 2]"#, { let mut v = vec![0, 0, 1, 2]; sort_colors(&mut v); v }, vec![0, 0, 1, 2]);
}

#[test]
fn reversed() {
    check!(r#"nums = [2, 2, 1, 1, 0, 0]"#, { let mut v = vec![2, 2, 1, 1, 0, 0]; sort_colors(&mut v); v }, vec![0, 0, 1, 1, 2, 2]);
}

#[test]
fn no_ones() {
    check!(r#"nums = [2, 0, 2, 0]"#, { let mut v = vec![2, 0, 2, 0]; sort_colors(&mut v); v }, vec![0, 0, 2, 2]);
}

#[test]
fn all_zeros() {
    check!(r#"nums = [0, 0, 0]"#, { let mut v = vec![0, 0, 0]; sort_colors(&mut v); v }, vec![0, 0, 0]);
}

#[test]
fn random_vs_sort() {
    let mut rng = anneal_prelude::Rng::new(17);
    for _ in 0..300 {
        let n = rng.below(12);
        let nums: Vec<u8> = rng.vec(n, 0, 2);
        let mut want = nums.clone();
        want.sort();
        let mut got = nums.clone();
        sort_colors(&mut got);
        check!(format!("nums = {nums:?}"), got, want);
    }
}

#[test]
fn scale_200k() {
    let mut rng = anneal_prelude::Rng::new(18);
    let mut v: Vec<u8> = rng.vec(200_000, 0, 2);
    let mut want = v.clone();
    want.sort();
    sort_colors(&mut v);
    check!("200000 random values in 0..=2", v == want, true);
}
