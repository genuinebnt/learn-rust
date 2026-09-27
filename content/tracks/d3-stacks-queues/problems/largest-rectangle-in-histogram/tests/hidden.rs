use solution::*;

#[test]
fn single() {
    check!(r#"[7]"#, largest_rectangle(&[7]), 7);
}

#[test]
fn increasing() {
    check!(r#"[1,2,3,4,5]"#, largest_rectangle(&[1, 2, 3, 4, 5]), 9);
}

#[test]
fn decreasing() {
    check!(r#"[5,4,3,2,1]"#, largest_rectangle(&[5, 4, 3, 2, 1]), 9);
}

#[test]
fn zeros() {
    check!(r#"[0,0]"#, largest_rectangle(&[0, 0]), 0);
}

#[test]
fn u32_max() {
    check!(r#"[u32::MAX]"#, largest_rectangle(&[u32::MAX]), 4_294_967_295);
}

#[test]
fn two_max() {
    check!(r#"[u32::MAX, u32::MAX]"#, largest_rectangle(&[u32::MAX, u32::MAX]), 8_589_934_590);
}

#[test]
fn classic() {
    check!(r#"[6,2,5,4,5,1,6]"#, largest_rectangle(&[6, 2, 5, 4, 5, 1, 6]), 12);
}

#[test]
fn dip() {
    check!(r#"[2,1,2]"#, largest_rectangle(&[2, 1, 2]), 3);
}

#[test]
fn zero_splits() {
    check!(r#"[4,2,0,3,2,5]"#, largest_rectangle(&[4, 2, 0, 3, 2, 5]), 6);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(3011);
    for _ in 0..300 {
        let n = rng.below(10);
        let h: Vec<u32> = rng.vec(n, 0, 6);
        let mut want = 0u64;
        for i in 0..n {
            let mut low = u32::MAX;
            for j in i..n {
                low = low.min(h[j]);
                want = want.max(u64::from(low) * (j - i + 1) as u64);
            }
        }
        check!(format!("heights = {h:?}"), largest_rectangle(&h), want);
    }
}

#[test]
fn scale_200k_increasing() {
    let h: Vec<u32> = (1..=200_000).collect();
    check!("heights = [1, 2, …, 200000]", largest_rectangle(&h), 10_000_100_000);
}

#[test]
fn huge() {
    let h = vec![1_000_000_000u32; 100_000];
    check!(r#"10⁵ bars of height 10⁹"#, largest_rectangle(&h), 100_000_000_000_000);
}
