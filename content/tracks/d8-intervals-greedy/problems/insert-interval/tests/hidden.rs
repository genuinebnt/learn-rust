use solution::*;

#[test]
fn covers_all() {
    check!(r#"intervals = [(1, 2), (4, 5), (7, 8)], new = (0, 10)"#, insert(&[(1, 2), (4, 5), (7, 8)], (0, 10)), vec![(0, 10)]);
}

#[test]
fn inside_one() {
    check!(r#"intervals = [(1, 10)], new = (3, 4)"#, insert(&[(1, 10)], (3, 4)), vec![(1, 10)]);
}

#[test]
fn in_a_gap() {
    check!(r#"intervals = [(1, 2), (8, 9)], new = (4, 5)"#, insert(&[(1, 2), (8, 9)], (4, 5)), vec![(1, 2), (4, 5), (8, 9)]);
}

#[test]
fn touches_both_sides() {
    check!(r#"intervals = [(1, 3), (5, 7)], new = (3, 5)"#, insert(&[(1, 3), (5, 7)], (3, 5)), vec![(1, 7)]);
}

#[test]
fn point_in_gap() {
    check!(r#"intervals = [(1, 3), (5, 7)], new = (4, 4)"#, insert(&[(1, 3), (5, 7)], (4, 4)), vec![(1, 3), (4, 4), (5, 7)]);
}

#[test]
fn touches_left_neighbour() {
    check!(r#"intervals = [(1, 3), (8, 9)], new = (3, 5)"#, insert(&[(1, 3), (8, 9)], (3, 5)), vec![(1, 5), (8, 9)]);
}

#[test]
fn i32_extremes_apart() {
    check!(r#"intervals = [(i32::MIN, -1), (1, i32::MAX)], new = (0, 0)"#, insert(&[(i32::MIN, -1), (1, i32::MAX)], (0, 0)), vec![(i32::MIN, -1), (0, 0), (1, i32::MAX)]);
}

#[test]
fn i32_extremes_join() {
    check!(r#"intervals = [(i32::MIN, -1), (1, i32::MAX)], new = (-1, 1)"#, insert(&[(i32::MIN, -1), (1, i32::MAX)], (-1, 1)), vec![(i32::MIN, i32::MAX)]);
}

#[test]
fn same_as_existing() {
    check!(r#"intervals = [(2, 4)], new = (2, 4)"#, insert(&[(2, 4)], (2, 4)), vec![(2, 4)]);
}

fn grid_merge(intervals: &[(i32, i32)]) -> Vec<(i32, i32)> {
    let mut marked = vec![false; 64];
    for &(s, e) in intervals {
        for x in 2 * s..=2 * e {
            marked[x as usize] = true;
        }
    }
    let mut out = Vec::new();
    let mut x = 0;
    while x < marked.len() {
        if marked[x] {
            let start = x;
            while x + 1 < marked.len() && marked[x + 1] {
                x += 1;
            }
            out.push((start as i32 / 2, x as i32 / 2));
        }
        x += 1;
    }
    out
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(808);
    for _ in 0..400 {
        let n = rng.below(7);
        let raw: Vec<(i32, i32)> = (0..n)
            .map(|_| {
                let s = rng.int(0, 25) as i32;
                let len = rng.int(0, 3) as i32;
                (s, s + len)
            })
            .collect();
        let intervals = grid_merge(&raw);
        let s = rng.int(0, 25) as i32;
        let len = rng.int(0, 5) as i32;
        let new = (s, s + len);
        let mut all = intervals.clone();
        all.push(new);
        check!(format!("intervals = {intervals:?}, new = {new:?}"), insert(&intervals, new), grid_merge(&all));
    }
}

#[test]
fn scale_200k() {
    let intervals: Vec<(i32, i32)> = (0..200_000).map(|i| (3 * i, 3 * i + 1)).collect();
    let out = insert(&intervals, (1, 300_000));
    check!("(3i, 3i + 1) for i in 0..200000, new = (1, 300000)", (out.len(), out[0], out[1]), (100_000, (0, 300_001), (300_003, 300_004)));
}
