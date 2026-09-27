use solution::*;

#[test]
fn falling() {
    check!(r#"people = [(1, 2), (2, 1), (3, 0)]"#, reconstruct_queue(&[(1, 2), (2, 1), (3, 0)]), vec![(3, 0), (2, 1), (1, 2)]);
}

#[test]
fn all_same_height() {
    check!(r#"people = [(4, 2), (4, 1), (4, 0)]"#, reconstruct_queue(&[(4, 2), (4, 1), (4, 0)]), vec![(4, 0), (4, 1), (4, 2)]);
}

#[test]
fn short_one_first() {
    check!(r#"people = [(9, 0), (1, 0)]"#, reconstruct_queue(&[(9, 0), (1, 0)]), vec![(1, 0), (9, 0)]);
}

#[test]
fn u32_heights() {
    check!(r#"people = [(0, 2), (4294967295, 1), (4294967295, 0)]"#, reconstruct_queue(&[(0, 2), (u32::MAX, 1), (u32::MAX, 0)]), vec![(u32::MAX, 0), (u32::MAX, 1), (0, 2)]);
}

#[test]
fn zero_height() {
    check!(r#"people = [(0, 0), (0, 1)]"#, reconstruct_queue(&[(0, 0), (0, 1)]), vec![(0, 0), (0, 1)]);
}

#[test]
fn six_mixed() {
    check!(r#"people = [(4, 2), (1, 4), (5, 1), (3, 1), (5, 0), (2, 0)]"#, reconstruct_queue(&[(4, 2), (1, 4), (5, 1), (3, 1), (5, 0), (2, 0)]), vec![(2, 0), (5, 0), (3, 1), (5, 1), (1, 4), (4, 2)]);
}

#[test]
fn seven_mixed() {
    check!(r#"people = [(1, 6), (7, 0), (2, 4), (3, 2), (6, 1), (2, 1), (6, 0)]"#, reconstruct_queue(&[(1, 6), (7, 0), (2, 4), (3, 2), (6, 1), (2, 1), (6, 0)]), vec![(6, 0), (2, 1), (6, 1), (3, 2), (2, 4), (7, 0), (1, 6)]);
}

#[test]
fn equal_heights_then_short() {
    check!(r#"people = [(2, 1), (2, 0), (1, 2)]"#, reconstruct_queue(&[(2, 1), (2, 0), (1, 2)]), vec![(2, 0), (2, 1), (1, 2)]);
}

/// The (h, k) pairs of a queue given front to back.
fn describe(heights: &[u32]) -> Vec<(u32, usize)> {
    (0..heights.len()).map(|i| (heights[i], heights[..i].iter().filter(|&&h| h >= heights[i]).count())).collect()
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(822);
    for _ in 0..400 {
        let n = rng.below(9);
        let heights: Vec<u32> = rng.vec(n, 1, 5);
        let queue = describe(&heights);
        let mut people = queue.clone();
        rng.shuffle(&mut people);
        check!(format!("people = {people:?}"), reconstruct_queue(&people), queue);
    }
}

#[test]
fn scale_10k() {
    let heights: Vec<u32> = (0..10_000u32).map(|i| i * 7919 % 10_007 % 500).collect();
    let queue = describe(&heights);
    let people: Vec<(u32, usize)> = queue.iter().rev().copied().collect();
    check!("10000 people, heights (7919 i mod 10007) mod 500, given back to front", reconstruct_queue(&people) == queue, true);
}
