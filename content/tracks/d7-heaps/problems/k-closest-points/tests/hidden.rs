use solution::*;

#[test]
fn empty() {
    check!(r#"points = [], k = 3"#, k_closest(&[], 3), Vec::<(i32, i32)>::new());
}

#[test]
fn origin() {
    check!(r#"points = [(0, 0), (0, 1)], k = 1"#, k_closest(&[(0, 0), (0, 1)], 1), vec![(0, 0)]);
}

#[test]
fn past_i32_squares() {
    check!(r#"points = [(50000, 0), (0, 46341)], k = 1"#, k_closest(&[(50_000, 0), (0, 46_341)], 1), vec![(0, 46_341)]);
}

#[test]
fn the_i32_corners() {
    check!(r#"points = [(i32::MIN, i32::MIN), (i32::MAX, i32::MAX), (0, 0)], k = 3"#, k_closest(&[(i32::MIN, i32::MIN), (i32::MAX, i32::MAX), (0, 0)], 3), vec![(0, 0), (i32::MAX, i32::MAX), (i32::MIN, i32::MIN)]);
}

#[test]
fn min_corner_alone() {
    check!(r#"points = [(i32::MIN, i32::MIN)], k = 1"#, k_closest(&[(i32::MIN, i32::MIN)], 1), vec![(i32::MIN, i32::MIN)]);
}

#[test]
fn circle_of_25() {
    check!(r#"points = [(3, -4), (5, 0), (-3, 4), (0, 5), (4, 3), (-5, 0)], k = 4"#, k_closest(&[(3, -4), (5, 0), (-3, 4), (0, 5), (4, 3), (-5, 0)], 4), vec![(-5, 0), (-3, 4), (0, 5), (3, -4)]);
}

#[test]
fn negative_x_is_not_nearer() {
    check!(r#"points = [(-3, 0), (2, 2)], k = 1 (9 > 8)"#, k_closest(&[(-3, 0), (2, 2)], 1), vec![(2, 2)]);
}

#[test]
fn k_equals_len() {
    check!(r#"points = [(5, 5), (-1, -1), (2, -2)], k = 3"#, k_closest(&[(5, 5), (-1, -1), (2, -2)], 3), vec![(-1, -1), (2, -2), (5, 5)]);
}

#[test]
fn all_same_point() {
    check!(r#"points = [(7, 7); 4], k = 2"#, k_closest(&[(7, 7); 4], 2), vec![(7, 7), (7, 7)]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(707);
    for _ in 0..300 {
        let n = rng.below(10);
        let points: Vec<(i32, i32)> = (0..n).map(|_| (rng.int(-3, 3) as i32, rng.int(-3, 3) as i32)).collect();
        let k = rng.below(12);
        let mut want = points.clone();
        want.sort_by_key(|&(x, y)| (x * x + y * y, x, y));
        want.truncate(k);
        check!(format!("points = {points:?}, k = {k}"), k_closest(&points, k), want);
    }
}

#[test]
fn scale_200k_points() {
    let mut rng = anneal_prelude::Rng::new(708);
    let points: Vec<(i32, i32)> = (0..200_000).map(|_| (rng.int(-1000, 1000) as i32, rng.int(-1000, 1000) as i32)).collect();
    let mut want = points.clone();
    want.sort_unstable_by_key(|&(x, y)| (x as i64 * x as i64 + y as i64 * y as i64, x, y));
    want.truncate(100_000);
    let got = k_closest(&points, 100_000);
    check!("200000 random points in [-1000, 1000]², k = 100000; first wrong index", got.iter().zip(&want).position(|(a, b)| a != b).or((got.len() != want.len()).then_some(got.len())), None);
}
