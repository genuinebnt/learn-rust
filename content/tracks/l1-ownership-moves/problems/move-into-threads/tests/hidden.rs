use solution::*;

#[test]
fn many() {
    check!(r#"8 chunks of 0..1000"#, parallel_sum((0..8).map(|_| (0..1000).collect()).collect()), 8 * 499_500);
}

#[test]
fn empty_chunks_inside() {
    check!(r#"[[], [1], []]"#, parallel_sum(vec![vec![], vec![1], vec![]]), 1);
}

#[test]
fn only_empty_chunks() {
    check!(r#"[[], []]"#, parallel_sum(vec![vec![], vec![]]), 0);
}

#[test]
fn beyond_u32() {
    check!(r#"[[5000000000], [5000000000]]"#, parallel_sum(vec![vec![5_000_000_000], vec![5_000_000_000]]), 10_000_000_000);
}

#[test]
fn near_u64_max() {
    check!(r#"[[u64::MAX / 2], [u64::MAX / 2]]"#, parallel_sum(vec![vec![u64::MAX / 2], vec![u64::MAX / 2]]), u64::MAX - 1);
}

#[test]
fn sixty_four_chunks() {
    check!(r#"64 chunks [i]"#, parallel_sum((0..64).map(|i| vec![i]).collect()), 2016);
}

#[test]
fn one_big_chunk() {
    check!(r#"[1..=200000]"#, parallel_sum(vec![(1..=200_000).collect()]), 20_000_100_000);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1112);
    for _ in 0..100 {
        let k = rng.below(6);
        let mut chunks: Vec<Vec<u64>> = Vec::new();
        for _ in 0..k {
            let len = rng.below(8);
            chunks.push(rng.vec(len, 0, 1_000_000_000_000));
        }
        let want: u64 = chunks.iter().flatten().sum();
        check!(format!("chunks = {chunks:?}"), parallel_sum(chunks.clone()), want);
    }
}
