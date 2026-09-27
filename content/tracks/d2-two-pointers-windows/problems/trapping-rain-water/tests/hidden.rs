use solution::*;

#[test]
fn empty() {
    check!(r#"heights = []"#, trap(&[]), 0);
}

#[test]
fn monotonic() {
    check!(r#"heights = [1, 2, 3, 4]"#, trap(&[1, 2, 3, 4]), 0);
}

#[test]
fn tall_walls() {
    check!(r#"heights = [u32::MAX, 0, u32::MAX]"#, trap(&[u32::MAX, 0, u32::MAX]), u32::MAX as u64);
}

#[test]
fn single() {
    check!(r#"heights = [7]"#, trap(&[7]), 0);
}

#[test]
fn two() {
    check!(r#"heights = [3, 0]"#, trap(&[3, 0]), 0);
}

#[test]
fn descending() {
    check!(r#"heights = [4, 3, 2, 1]"#, trap(&[4, 3, 2, 1]), 0);
}

#[test]
fn uneven_walls() {
    check!(r#"heights = [3, 0, 1]"#, trap(&[3, 0, 1]), 1);
}

#[test]
fn plateau() {
    check!(r#"heights = [2, 0, 0, 2]"#, trap(&[2, 0, 0, 2]), 4);
}

#[test]
fn total_past_u32() {
    check!(r#"heights = [u32::MAX, 0, 0, u32::MAX]"#, trap(&[u32::MAX, 0, 0, u32::MAX]), 2 * u32::MAX as u64);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(217);
    for _ in 0..300 {
        let n = rng.below(14);
        let heights: Vec<u32> = rng.vec(n, 0, 6);
        let want: u64 = (0..n)
            .map(|i| {
                let left = *heights[..=i].iter().max().unwrap();
                let right = *heights[i..].iter().max().unwrap();
                (left.min(right) - heights[i]) as u64
            })
            .sum();
        check!(format!("heights = {heights:?}"), trap(&heights), want);
    }
}

#[test]
fn scale_200k() {
    let heights: Vec<u32> = (0..200_000u64).map(|i| (i * 7919 % 100_003) as u32).collect();
    check!("heights[i] = i * 7919 % 100003 for i in 0..200000", trap(&heights), 9_997_919_672);
}
