use solution::*;

#[test]
fn touch_once() {
    check!(r#"points = [(1, 2), (2, 3)]"#, find_min_arrow_shots(&[(1, 2), (2, 3)]), 1);
}

#[test]
fn points_only() {
    check!(r#"points = [(5, 5), (5, 5)]"#, find_min_arrow_shots(&[(5, 5), (5, 5)]), 1);
}

#[test]
fn i32_whole_line() {
    check!(r#"points = [(MIN, MAX), (MAX, MAX)]"#, find_min_arrow_shots(&[(i32::MIN, i32::MAX), (i32::MAX, i32::MAX)]), 1);
}

#[test]
fn i32_far_ends() {
    check!(r#"points = [(MIN, MIN), (MAX, MAX)]"#, find_min_arrow_shots(&[(i32::MIN, i32::MIN), (i32::MAX, i32::MAX)]), 2);
}

#[test]
fn leetcode_overflow() {
    check!(r#"points = [(-2147483646, -2147483645), (2147483646, 2147483647)]"#, find_min_arrow_shots(&[(-2147483646, -2147483645), (2147483646, 2147483647)]), 2);
}

#[test]
fn start_sort_trap() {
    check!(r#"points = [(1, 10), (2, 3), (4, 5)]"#, find_min_arrow_shots(&[(1, 10), (2, 3), (4, 5)]), 2);
}

#[test]
fn negatives() {
    check!(r#"points = [(-5, -3), (-4, 0), (1, 2)]"#, find_min_arrow_shots(&[(-5, -3), (-4, 0), (1, 2)]), 2);
}

#[test]
fn duplicates() {
    check!(r#"points = [(1, 3), (1, 3), (1, 3), (4, 4)]"#, find_min_arrow_shots(&[(1, 3), (1, 3), (1, 3), (4, 4)]), 2);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(810);
    for _ in 0..300 {
        let n = rng.below(8);
        let points: Vec<(i32, i32)> = (0..n)
            .map(|_| {
                let s = rng.int(-5, 15) as i32;
                let len = rng.int(0, 5) as i32;
                (s, s + len)
            })
            .collect();
        // Some best set of arrows sits at balloon ends: try every subset of ends.
        let mut want = n;
        for mask in 0u32..1 << n {
            let shots: Vec<i32> = (0..n).filter(|&i| mask >> i & 1 == 1).map(|i| points[i].1).collect();
            if points.iter().all(|&(s, e)| shots.iter().any(|&x| s <= x && x <= e)) {
                want = want.min(shots.len());
            }
        }
        check!(format!("points = {points:?}"), find_min_arrow_shots(&points), want);
    }
}

#[test]
fn scale_200k() {
    let points: Vec<(i32, i32)> = (0..200_000).rev().map(|i| (2 * i, 2 * i + 1)).collect();
    check!("(2i, 2i + 1) for i in 0..200000, reversed", find_min_arrow_shots(&points), 200_000);
}
