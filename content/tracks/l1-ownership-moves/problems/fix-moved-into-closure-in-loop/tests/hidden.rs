use solution::*;

#[test]
fn big() {
    check!(r#"data = 0..10000, n = 4"#, sum_everywhere((0..10_000).collect(), 4), vec![49_995_000; 4]);
}

#[test]
fn empty_data() {
    check!(r#"data = [], n = 3"#, sum_everywhere(vec![], 3), vec![0, 0, 0]);
}

#[test]
fn single_value() {
    check!(r#"data = [9], n = 2"#, sum_everywhere(vec![9], 2), vec![9, 9]);
}

#[test]
fn uneven_split() {
    check!(r#"data = [1, 2, 3, 4, 5], n = 2"#, sum_everywhere(vec![1, 2, 3, 4, 5], 2), vec![15, 15]);
}

#[test]
fn sixteen_threads() {
    check!(r#"data = [1, 1, 1], n = 16"#, sum_everywhere(vec![1, 1, 1], 16), vec![3; 16]);
}

#[test]
fn large_values() {
    check!(r#"data = [u64::MAX / 4; 2], n = 2"#, sum_everywhere(vec![u64::MAX / 4; 2], 2), vec![u64::MAX / 4 * 2; 2]);
}

#[test]
fn empty_no_threads() {
    check!(r#"data = [], n = 0"#, sum_everywhere(vec![], 0), Vec::<u64>::new());
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1113);
    for _ in 0..100 {
        let len = rng.below(10);
        let data: Vec<u64> = rng.vec(len, 0, 1_000_000);
        let n = rng.below(5);
        let want = vec![data.iter().sum::<u64>(); n];
        check!(format!("data = {data:?}, n = {n}"), sum_everywhere(data.clone(), n), want);
    }
}
