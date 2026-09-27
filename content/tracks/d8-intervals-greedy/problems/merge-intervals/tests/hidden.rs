use solution::*;

#[test]
fn points() {
    check!(r#"intervals = [(5, 5), (5, 5)]"#, merge(&[(5, 5), (5, 5)]), vec![(5, 5)]);
}

#[test]
fn gap_of_one_stays_apart() {
    check!(r#"intervals = [(1, 2), (3, 4)]"#, merge(&[(1, 2), (3, 4)]), vec![(1, 2), (3, 4)]);
}

#[test]
fn negatives() {
    check!(r#"intervals = [(-3, -1), (-2, 0)]"#, merge(&[(-3, -1), (-2, 0)]), vec![(-3, 0)]);
}

#[test]
fn i32_extremes() {
    check!(r#"intervals = [(i32::MIN, 0), (0, i32::MAX)]"#, merge(&[(i32::MIN, 0), (0, i32::MAX)]), vec![(i32::MIN, i32::MAX)]);
}

#[test]
fn contained_then_longer() {
    check!(r#"intervals = [(1, 10), (2, 3), (4, 11)]"#, merge(&[(1, 10), (2, 3), (4, 11)]), vec![(1, 11)]);
}

#[test]
fn chain() {
    check!(r#"intervals = [(3, 4), (1, 2), (2, 3)]"#, merge(&[(3, 4), (1, 2), (2, 3)]), vec![(1, 4)]);
}

#[test]
fn duplicates() {
    check!(r#"intervals = [(1, 3), (1, 3)]"#, merge(&[(1, 3), (1, 3)]), vec![(1, 3)]);
}

#[test]
fn long_one_last() {
    check!(r#"intervals = [(2, 3), (5, 6), (1, 10)]"#, merge(&[(2, 3), (5, 6), (1, 10)]), vec![(1, 10)]);
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
    let mut rng = anneal_prelude::Rng::new(807);
    for _ in 0..400 {
        let n = rng.below(8);
        let intervals: Vec<(i32, i32)> = (0..n)
            .map(|_| {
                let s = rng.int(0, 25) as i32;
                let len = rng.int(0, 5) as i32;
                (s, s + len)
            })
            .collect();
        check!(format!("intervals = {intervals:?}"), merge(&intervals), grid_merge(&intervals));
    }
}

#[test]
fn scale_200k() {
    // 199999 separate intervals in reverse order, plus one that joins the first two.
    let mut intervals: Vec<(i32, i32)> = (0..199_999).rev().map(|i| (3 * i, 3 * i + 1)).collect();
    intervals.push((1, 3));
    let out = merge(&intervals);
    check!("(3i, 3i + 1) for i in 0..199999, reversed, plus (1, 3)", (out.len(), out[0], out[1], out[out.len() - 1]), (199_998, (0, 4), (6, 7), (599_994, 599_995)));
}
