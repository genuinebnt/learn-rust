use solution::*;

#[test]
fn one_row() {
    check!(r#"triangle = [[7]]"#, minimum_total(&[vec![7]]), 7);
}

#[test]
fn zeros() {
    check!(r#"triangle = [[0], [0, 0]]"#, minimum_total(&[vec![0], vec![0, 0]]), 0);
}

#[test]
fn greedy_trap() {
    check!(r#"triangle = [[1], [2, 3], [100, 100, 1]]"#, minimum_total(&[vec![1], vec![2, 3], vec![100, 100, 1]]), 5);
}

#[test]
fn not_row_minimums() {
    check!(r#"triangle = [[-1], [2, 3], [1, -1, -3]]"#, minimum_total(&[vec![-1], vec![2, 3], vec![1, -1, -3]]), -1);
}

#[test]
fn all_max() {
    check!(r#"triangle = [[10000], [10000, 10000]]"#, minimum_total(&[vec![10_000], vec![10_000, 10_000]]), 20_000);
}

#[test]
fn all_min() {
    check!(r#"triangle = [[-10000], [-10000, -10000], [-10000, -10000, -10000]]"#, minimum_total(&[vec![-10_000], vec![-10_000, -10_000], vec![-10_000, -10_000, -10_000]]), -30_000);
}

#[test]
fn deep_negative() {
    check!(r#"triangle = 1000 rows of -10000"#, minimum_total(&(1..=1000).map(|r| vec![-10_000; r]).collect::<Vec<_>>()), -10_000_000);
}

#[test]
fn random_vs_brute_force() {
    fn walk(t: &[Vec<i32>], r: usize, c: usize) -> i64 {
        let here = t[r][c] as i64;
        if r + 1 == t.len() { here } else { here + walk(t, r + 1, c).min(walk(t, r + 1, c + 1)) }
    }
    let mut rng = anneal_prelude::Rng::new(1221);
    for _ in 0..300 {
        let rows = rng.int(1, 10) as usize;
        let tri: Vec<Vec<i32>> = (1..=rows).map(|len| rng.vec(len, -9, 9)).collect();
        check!(format!("triangle = {tri:?}"), minimum_total(&tri), walk(&tri, 0, 0));
    }
}

#[test]
fn scale_2000_rows() {
    let tri: Vec<Vec<i32>> = (0..2000i32).map(|r| (0..=r).map(|c| (r * 7 + c * 13) % 201 - 100).collect()).collect();
    check!("triangle[r][c] = (7r + 13c) % 201 - 100, 2000 rows", minimum_total(&tri), -58_605);
}
