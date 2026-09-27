use solution::*;

#[test]
fn no_cuts() {
    check!(r#"n = 5, cuts = []"#, min_cost(5, &[]), 0);
}

#[test]
fn middle() {
    check!(r#"n = 100, cuts = [50]"#, min_cost(100, &[50]), 100);
}

#[test]
fn reversed_input() {
    check!(r#"n = 10, cuts = [5, 2]"#, min_cost(10, &[5, 2]), 15);
}

#[test]
fn near_the_ends() {
    check!(r#"n = 1000000, cuts = [1, 999999]"#, min_cost(1_000_000, &[1, 999_999]), 1_999_999);
}

#[test]
fn every_point() {
    check!(r#"n = 5, cuts = [1, 2, 3, 4]"#, min_cost(5, &[1, 2, 3, 4]), 12);
}

#[test]
fn nineteen_cuts() {
    check!(r#"n = 30, cuts = [13, 25, 16, 20, 26, 5, 27, 8, 23, 14, 6, 15, 21, 24, 29, 1, 19, 9, 3]"#, min_cost(30, &[13, 25, 16, 20, 26, 5, 27, 8, 23, 14, 6, 15, 21, 24, 29, 1, 19, 9, 3]), 127);
}

#[test]
fn unsorted_six() {
    check!(r#"n = 20, cuts = [17, 3, 11, 8, 14, 5]"#, min_cost(20, &[17, 3, 11, 8, 14, 5]), 57);
}

#[test]
fn random_vs_brute_force() {
    // Try every cut first on the piece [lo, hi], then recurse on both halves.
    fn cheapest(lo: u32, hi: u32, cuts: &[u32]) -> u64 {
        let inside: Vec<u32> = cuts.iter().copied().filter(|&c| lo < c && c < hi).collect();
        inside.iter().map(|&c| (hi - lo) as u64 + cheapest(lo, c, &inside) + cheapest(c, hi, &inside)).min().unwrap_or(0)
    }
    let mut rng = anneal_prelude::Rng::new(1244);
    for _ in 0..300 {
        let n = rng.int(2, 15) as u32;
        let mut cuts: Vec<u32> = (1..n).filter(|_| rng.below(3) == 0).collect();
        cuts.truncate(6);
        rng.shuffle(&mut cuts);
        check!(format!("n = {n}, cuts = {cuts:?}"), min_cost(n, &cuts), cheapest(0, n, &cuts));
    }
}

#[test]
fn scale_200_cuts() {
    let cuts: Vec<u32> = (0..200u32).map(|i| i * 7919 % 999_999 + 1).collect();
    check!("n = 1000000, cuts[i] = (7919·i) % 999999 + 1, 200 cuts", min_cost(1_000_000, &cuts), 7_575_883);
}
