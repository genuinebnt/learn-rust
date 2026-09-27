use solution::*;

#[test]
fn one_line() {
    check!(r#"heights = [5]"#, max_area(&[5]), 0);
}

#[test]
fn large() {
    check!(r#"heights = [u32::MAX, u32::MAX]"#, max_area(&[u32::MAX, u32::MAX]), u32::MAX as u64);
}

#[test]
fn empty() {
    check!(r#"heights = []"#, max_area(&[]), 0);
}

#[test]
fn uneven_pair() {
    check!(r#"heights = [1, 5]"#, max_area(&[1, 5]), 1);
}

#[test]
fn zeros() {
    check!(r#"heights = [0, 0, 0]"#, max_area(&[0, 0, 0]), 0);
}

#[test]
fn descending() {
    check!(r#"heights = [5, 4, 3, 2, 1]"#, max_area(&[5, 4, 3, 2, 1]), 6);
}

#[test]
fn equal_walls() {
    check!(r#"heights = [2, 3, 4, 5, 18, 17, 6]"#, max_area(&[2, 3, 4, 5, 18, 17, 6]), 17);
}

#[test]
fn area_past_u32() {
    check!(r#"heights = [u32::MAX, 0, u32::MAX]"#, max_area(&[u32::MAX, 0, u32::MAX]), 2 * u32::MAX as u64);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(209);
    for _ in 0..300 {
        let n = rng.below(12);
        let heights: Vec<u32> = rng.vec(n, 0, 20);
        let mut want = 0u64;
        for i in 0..n {
            for j in i + 1..n {
                want = want.max(heights[i].min(heights[j]) as u64 * (j - i) as u64);
            }
        }
        check!(format!("heights = {heights:?}"), max_area(&heights), want);
    }
}

#[test]
fn scale_200k() {
    let heights: Vec<u32> = (0..200_000u64).map(|i| (i * 7919 % 100_003) as u32).collect();
    check!("heights[i] = i * 7919 % 100003 for i in 0..200000", max_area(&heights), 19_906_008_474);
}
